"""working.py - working memory: facts of the day / week.

Append-only storage for summaries (L1), inner voice (L2), dreams (L3).
Older facts get archived flag (not deleted).

Files:
  facts.jsonl  - append-only, all facts
  index.json   - stats

API:
  add_fact(text, origin, confidence, tags, date) -> dict
  get_active(days) -> list
  get_all() -> list
  prune(max_days) -> int
  stats() -> dict
"""
import os
import json
import time
import uuid

X = "X:" + os.sep
DIR = os.path.join(X, "03_memory_working")
FACTS = os.path.join(DIR, "facts.jsonl")
INDEX = os.path.join(DIR, "index.json")


def _ensure_dir():
    if not os.path.isdir(DIR):
        os.makedirs(DIR, exist_ok=True)


def _new_id():
    return uuid.uuid4().hex[:12]


def _today():
    return time.strftime("%Y-%m-%d")


def add_fact(text, origin="diary", confidence="low", tags=None, date=None):
    """Append one fact. origin: diary | inner_voice | dream."""
    if not text:
        return None
    _ensure_dir()
    ts = round(time.time(), 3)
    rec = {
        "id": _new_id(),
        "ts": ts,
        "date": date or _today(),
        "origin": origin,
        "confidence": confidence,
        "tags": tags or [],
        "text": text,
        "archived": False,
    }
    with open(FACTS, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    _rebuild_index()
    return rec


def _iter_all():
    if not os.path.exists(FACTS):
        return
    with open(FACTS, "r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def get_all():
    return list(_iter_all())


def get_active(days=7):
    """Return facts from last N days, not archived."""
    cutoff = time.time() - days * 86400
    out = []
    for r in _iter_all():
        if r.get("archived"):
            continue
        if r.get("ts", 0) >= cutoff:
            out.append(r)
    return out


def get_by_origin(origin, days=7):
    return [r for r in get_active(days) if r.get("origin") == origin]


def prune(max_days=30):
    """Mark facts older than max_days as archived. Never deletes."""
    cutoff = time.time() - max_days * 86400
    all_recs = []
    changed = 0
    for r in _iter_all():
        if not r.get("archived") and r.get("ts", 0) < cutoff:
            r["archived"] = True
            changed += 1
        all_recs.append(r)
    if changed:
        with open(FACTS, "w", encoding="utf-8") as f:
            for r in all_recs:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        _rebuild_index()
    return changed


def _rebuild_index():
    all_recs = list(_iter_all())
    active = [r for r in all_recs if not r.get("archived")]
    by_origin = {}
    for r in active:
        o = r.get("origin", "?")
        by_origin[o] = by_origin.get(o, 0) + 1
    idx = {
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "total": len(all_recs),
        "active": len(active),
        "archived": len(all_recs) - len(active),
        "by_origin": by_origin,
    }
    _ensure_dir()
    with open(INDEX, "w", encoding="utf-8") as f:
        json.dump(idx, f, ensure_ascii=False, indent=2)


def stats():
    if not os.path.exists(INDEX):
        _rebuild_index()
    with open(INDEX, "r", encoding="utf-8-sig") as f:
        return json.load(f)


if __name__ == "__main__":
    print("working.py - module. stats:", stats())
