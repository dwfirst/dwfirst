"""
storage.py - session storage for IRIS.

Two files:
  session.log   - append-only, ALL messages of current session (originals)
  window.jsonl  - working window (what actually goes to model), can be rewritten

Principle: originals never deleted from session.log. Window is a cache.
"""
import os
import json
import time
import uuid

X = "X:" + os.sep
DIR = os.path.join(X, "02_memory_fast")
SESSION_LOG = os.path.join(DIR, "session.log")
WINDOW_FILE = os.path.join(DIR, "window.jsonl")


def _ensure_dir():
    if not os.path.isdir(DIR):
        os.makedirs(DIR, exist_ok=True)


def _new_id():
    return uuid.uuid4().hex[:12]


def _session_id():
    return time.strftime("%Y-%m-%d") + "_001"


def append(role, content, tokens=0):
    """Append one message to session.log. Returns the record dict."""
    _ensure_dir()
    rec = {
        "id": _new_id(),
        "ts": round(time.time(), 3),
        "role": role,
        "content": content,
        "session_id": _session_id(),
        "tokens": tokens,
    }
    with open(SESSION_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return rec


def read_session():
    """Read all messages from session.log."""
    if not os.path.exists(SESSION_LOG):
        return []
    out = []
    with open(SESSION_LOG, "r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def read_window():
    """Read working window messages (without metadata)."""
    if not os.path.exists(WINDOW_FILE):
        return []
    out = []
    with open(WINDOW_FILE, "r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def write_window(messages):
    """Rewrite window.jsonl. messages is list of dicts with role+content."""
    _ensure_dir()
    with open(WINDOW_FILE, "w", encoding="utf-8") as f:
        for m in messages:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")


def window_to_chat(msgs=None):
    """Convert window records to chat format for llama_cpp."""
    if msgs is None:
        msgs = read_window()
    return [{"role": m["role"], "content": m["content"]} for m in msgs]


def reset_session():
    """Clear both session.log and window.jsonl. Use carefully."""
    _ensure_dir()
    if os.path.exists(SESSION_LOG):
        os.remove(SESSION_LOG)
    if os.path.exists(WINDOW_FILE):
        os.remove(WINDOW_FILE)


def stats():
    """Quick stats."""
    sess = read_session()
    win = read_window()
    return {
        "session_messages": len(sess),
        "window_messages": len(win),
        "session_path": SESSION_LOG,
        "window_path": WINDOW_FILE,
    }


if __name__ == "__main__":
    print("storage.py - module. stats:", stats())