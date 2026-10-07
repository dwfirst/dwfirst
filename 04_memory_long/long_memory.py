"""long_memory.py - append-only long-term archive for IRIS.

Every message ever, forever. Never deleted. Separate from session.log.
session.log = current session only.
archive.jsonl = all sessions, all time.

API:
  append(role, content, session_id, tokens) -> record
  get_by_id(msg_id) -> record or None
  get_by_date(date_str) -> list of records
  get_recent(n) -> list
  get_range(from_ts, to_ts) -> list
  stats() -> dict
"""
import os
import json
import time
import uuid

X = "X:" + os.sep
DIR = os.path.join(X, "04_memory_long")
ARCHIVE = os.path.join(DIR, "archive.jsonl")
INDEX = os.path.join(DIR, "index.json")


def _ensure_dir():
    if not os.path.isdir(DIR):
        os.makedirs(DIR, exist_ok=True)


def _new_id():
    return uuid.uuid4().hex[:12]


def _load_index():
    if not os.path.exists(INDEX):
        return {"total": 0, "first_ts": None, "last_ts": None, "days": []}
    with open(INDEX, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def _save_index(idx):
    _ensure_dir()
    with open(INDEX, "w", encoding="utf-8") as f:
        json.dump(idx, f, ensure_ascii=False, indent=2)


def append(role, content, session_id="", tokens=0):
    """Append one message to permanent archive. Never deletes."""
    _ensure_dir()
    ts = round(time.time(), 3)
    rec = {
        "id": _new_id(),
        "ts": ts,
        "date": time.strftime("%Y-%m-%d", time.localtime(ts)),
        "role": role,
        "content": content,
        "session_id": session_id,
        "tokens": tokens,
    }
    with open(ARCHIVE, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    idx = _load_index()
    idx["total"] += 1
    if idx["first_ts"] is None:
        idx["first_ts"] = ts
    idx["last_ts"] = ts
    if rec["date"] not in idx["days"]:
        idx["days"].append(rec["date"])
    _save_index(idx)
    return rec


def _iter_all():
    if not os.path.exists(ARCHIVE):
        return
    with open(ARCHIVE, "r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def get_by_id(msg_id):
    for rec in _iter_all():
        if rec["id"] == msg_id:
            return rec
    return None


def get_by_date(date_str):
    return [r for r in _iter_all() if r.get("date") == date_str]


def get_recent(n=20):
    all_recs = list(_iter_all())
    return all_recs[-n:]


def get_range(from_ts, to_ts):
    return [r for r in _iter_all() if from_ts <= r["ts"] <= to_ts]


def stats():
    idx = _load_index()
    size = os.path.getsize(ARCHIVE) if os.path.exists(ARCHIVE) else 0
    return {
        "total": idx["total"],
        "days": len(idx["days"]),
        "first_date": idx["days"][0] if idx["days"] else None,
        "last_date": idx["days"][-1] if idx["days"] else None,
        "archive_bytes": size,
        "archive_path": ARCHIVE,
    }


if __name__ == "__main__":
    print("long_memory.py - module. stats:", stats())
