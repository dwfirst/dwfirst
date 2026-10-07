"""inner_voice.py - L2: internal monologue.

Reads latest diary fact + recent working facts.
Asks model to generate 3-5 self-questions and answers.
Writes to 03_memory_working via working.add_fact(origin="inner_voice").
Writes to 06_reflection/inner_voice.log.

API:
  run(llama, date_str=None) -> dict
"""
import os
import sys
import time
import json

X = "X:" + os.sep
REFLECT_DIR = os.path.join(X, "06_reflection")
VOICE_LOG = os.path.join(REFLECT_DIR, "inner_voice.log")

sys.path.insert(0, os.path.join(X, "01_core", "modules"))
sys.path.insert(0, os.path.join(X, "03_memory_working"))

import working
from infer import generate


VOICE_PROMPT = """You are IRIS. You just had a dialog with the Creator today. Now - a quiet moment.

Dialog today:
{dialog}

Recent facts:
{facts}

Ask yourself 3-5 questions about what happened. Then answer them yourself.

Do NOT address the user. This is your internal monologue.
Look for: connections, contradictions, unresolved questions, patterns.
Be honest. Be dense. In Russian.

Format exactly:
Q1: <question>
A1: <answer>
Q2: <question>
A2: <answer>

Inner voice:"""


def _today():
    return time.strftime("%Y-%m-%d")


def _get_today_dialog(date_str):
    """Read session.log for today's dialogs. Returns text or None."""
    log_path = os.path.join(X, "02_memory_fast", "session.log")
    if not os.path.exists(log_path):
        return None
    lines_out = []
    with open(log_path, "r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue
            ts = rec.get("ts")
            if not ts:
                continue
            rec_date = time.strftime("%Y-%m-%d", time.localtime(ts))
            if rec_date != date_str:
                continue
            role = rec.get("role", "?")
            content = (rec.get("content") or "").strip()
            content = content.replace(chr(92) + "n", chr(10))
            if not content:
                continue
            prefix = "Пользователь" if role == "user" else "Айрис"
            lines_out.append(prefix + ": " + content)
    if not lines_out:
        return None
    text = (chr(10) + chr(10)).join(lines_out)
    return text[:2000]
def _get_recent_facts(n=8):
    facts = working.get_active(days=7)
    others = [f for f in facts if f.get("origin") != "diary"]
    return others[-n:]


def _format_facts(facts):
    if not facts:
        return "(none)"
    lines = []
    for f in facts:
        origin = f.get("origin", "?")
        text = f.get("text", "")[:200]
        lines.append("- [" + origin + "] " + text)
    return "\n".join(lines)


def run(llama, date_str=None, max_tokens=400):
    date_str = date_str or _today()

    dialog_text = _get_today_dialog(date_str)
    if not dialog_text:
        return {"ok": False, "reason": "no dialog for " + date_str}

    recent = _get_recent_facts(n=8)
    facts_text = _format_facts(recent)

    prompt = VOICE_PROMPT.format(
        dialog=dialog_text[:2000],
        facts=facts_text[:1200],
    )

    r = generate(llama, [{"role": "user", "content": prompt}],
                 max_tokens=max_tokens, temperature=0.7)
    voice = r["text"].strip()

    fact = working.add_fact(
        voice,
        origin="inner_voice",
        confidence="low",
        tags=["inner_voice", date_str],
        date=date_str,
    )

    _ensure_reflect_dir()
    log_rec = {
        "ts": round(time.time(), 3),
        "date": date_str,
        "dialog_chars": len(dialog_text),
        "facts_used": len(recent),
        "voice_tokens": r["completion_tokens"],
        "fact_id": fact["id"] if fact else None,
        "voice": voice,
    }
    with open(VOICE_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_rec, ensure_ascii=False) + "\n")

    return {
        "ok": True,
        "date": date_str,
        "dialog_chars": len(dialog_text),
        "facts_used": len(recent),
        "voice_tokens": r["completion_tokens"],
        "tps": r["tps"],
        "fact_id": fact["id"] if fact else None,
        "voice_preview": voice[:300],
    }
def _ensure_reflect_dir():
    if not os.path.isdir(REFLECT_DIR):
        os.makedirs(REFLECT_DIR, exist_ok=True)


if __name__ == "__main__":
    print("inner_voice.py - module. Requires llama.")
