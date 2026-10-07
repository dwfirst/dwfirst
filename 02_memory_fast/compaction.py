"""
compaction.py - sliding summarization for IRIS working window.

When window exceeds t_max tokens, oldest messages (up to t_retained) are
summarized by the model into one system message. Originals stay in session.log.

Principle: window is a cache. Archive is permanent.
"""
import os
import sys
import json

X = "X:" + os.sep
MODULES = os.path.join(X, "01_core", "modules")
MEM_FAST = os.path.join(X, "02_memory_fast")
for p in (MODULES, MEM_FAST):
    if p not in sys.path:
        sys.path.insert(0, p)

import storage
import counter


import json


def _load_compaction_config():
    """Read budget + compaction sections from config.json.

    window budget = t_max (when to trigger)
    t_retained = half of window budget (what stays verbatim)
    summary_tokens = compaction.summary_tokens
    """
    cfg_path = os.path.join(X, "00_dna", "config.json")
    defaults = {"t_max": 3000, "t_retained": 1500, "summary_tokens": 300}
    if not os.path.exists(cfg_path):
        return defaults
    try:
        with open(cfg_path, "r", encoding="utf-8-sig") as f:
            cfg = json.load(f)

        budget = cfg.get("budget", {})
        comp = cfg.get("compaction", {})

        window_budget = budget.get("window", 3000)
        t_max = comp.get("t_max", window_budget)
        # t_retained always less than t_max - guarantee progress
        t_retained = comp.get("t_retained", t_max // 2)
        if t_retained >= t_max:
            t_retained = t_max // 2

        return {
            "t_max": t_max,
            "t_retained": t_retained,
            "summary_tokens": comp.get("summary_tokens", 300),
        }
    except Exception:
        return defaults


_CFG = _load_compaction_config()
T_MAX = _CFG["t_max"]
T_RETAINED = _CFG["t_retained"]
SUMMARY_TOKENS = _CFG["summary_tokens"]


SUMMARY_PROMPT = (
    "You are a memory compressor. Summarize the following dialogue fragment "
    "in Russian, keeping: key facts, decisions made, open questions, named entities, "
    "and any commitments. Be dense and specific. "
    "Output only the summary, no preamble. Target: about {n} tokens."
)


def needs_compaction(llama, window, t_max=None):
    """Check if window exceeds t_max tokens. Default from config.json."""
    if t_max is None:
        t_max = T_MAX
    return counter.count_window(llama, window) > t_max


def _split_window(llama, window, t_retained=T_RETAINED):
    """
    Split window into (old_part, fresh_tail) where fresh_tail fits t_retained.
    Always keeps at least last 2 messages in fresh_tail.
    ALWAYS leaves at least half of window in old_part if window has >4 messages,
    otherwise compaction is a no-op and we loop forever.
    """
    n = len(window)
    if n <= 4:
        # Too small to compact - keep as is
        return [], list(window)

    # Compute t_retained cap: at most half of window tokens, but never more than configured
    total_tokens = counter.count_window(llama, window)
    effective_retained = min(t_retained, total_tokens // 2)

    fresh = []
    total = 0
    for m in reversed(window):
        mt = counter.count_message(llama, m)
        if total + mt > effective_retained and len(fresh) >= 2:
            break
        fresh.insert(0, m)
        total += mt

    # Guarantee: old_part must be non-empty if we have more than 4 messages
    if len(fresh) >= n:
        fresh = fresh[-max(2, n // 2):]

    old = window[:len(window) - len(fresh)]
    return old, fresh


def _build_summary_messages(old_part):
    """Build chat messages for the summarizer."""
    text = ""
    for m in old_part:
        role = m.get("role", "?")
        content = m.get("content", "")
        text += role + ": " + content + "\n"
    user = SUMMARY_PROMPT.format(n=SUMMARY_TOKENS) + "\n\n---\n" + text
    return [{"role": "user", "content": user}]


def compact(llama, window, summary_tokens=None, t_retained=None):
    if summary_tokens is None:
        summary_tokens = SUMMARY_TOKENS
    if t_retained is None:
        t_retained = T_RETAINED
    """
    Compact old part of window into one system message.
    Returns (new_window, summary_text, stats).
    """
    old, fresh = _split_window(llama, window, t_retained=t_retained)
    if not old:
        return list(window), "", {"skipped": True, "reason": "nothing to compact"}

    # Import infer lazily to avoid circular deps
    from infer import generate
    msgs = _build_summary_messages(old)
    r = generate(llama, msgs, max_tokens=summary_tokens, temperature=0.3)
    summary_text = r["text"].strip()

    new_window = [{"role": "system", "content": "[СВОДКА ИСТОРИИ] " + summary_text}]
    new_window.extend(fresh)

    stats = {
        "old_messages": len(old),
        "fresh_messages": len(fresh),
        "summary_tokens": counter.count_text(llama, summary_text),
        "new_window_tokens": counter.count_window(llama, new_window),
    }
    return new_window, summary_text, stats


def compact_and_save(llama, summary_tokens=None, t_retained=None):
    if summary_tokens is None:
        summary_tokens = SUMMARY_TOKENS
    if t_retained is None:
        t_retained = T_RETAINED
    """
    High-level: read window, compact, write back. Returns stats.
    Originals in session.log untouched.
    """
    window = storage.read_window()
    if not window:
        return {"ok": False, "reason": "empty window"}
    new_window, summary_text, stats = compact(llama, window, summary_tokens, t_retained)
    storage.write_window(new_window)
    stats["ok"] = True
    stats["summary_preview"] = summary_text[:200]
    return stats


if __name__ == "__main__":
    print("compaction.py - module. Requires llama.")