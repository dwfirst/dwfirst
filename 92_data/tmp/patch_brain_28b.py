# patch_brain_28b.py - dobavlyaem _index_dialog i vyzov v chat_one
import io, os

X = "X:" + os.sep
p = os.path.join(X, "01_core", "modules", "brain.py")

with io.open(p, "r", encoding="utf-8-sig") as f:
    src = f.read()

# === 1) vstavka funkciy _load_hashes, _save_hashes, _index_dialog pered chat_one ===
marker1 = "def chat_one(user_text"
if marker1 not in src:
    raise SystemExit("chat_one anchor not found")

block = '''def _load_hashes():
    """Load ingested_hashes.json from Chroma."""
    import json as _json
    path = os.path.join(X, "05_chroma", "ingested_hashes.json")
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            return _json.load(f)
    except Exception:
        return {}


def _save_hashes(hashes):
    """Save ingested_hashes.json."""
    import json as _json
    path = os.path.join(X, "05_chroma", "ingested_hashes.json")
    with open(path, "w", encoding="utf-8") as f:
        _json.dump(hashes, f, ensure_ascii=False, indent=2)


def _index_dialog(user_text, assistant_text, session_id=""):
    """Index a user+assistant pair into Chroma. Idempotent. Skips tests."""
    if chroma_store is None:
        return {"ok": False, "reason": "no chroma"}
    if not user_text or not assistant_text:
        return {"ok": False, "reason": "empty"}
    if session_id.startswith("test_"):
        return {"ok": False, "reason": "test session skipped"}

    import hashlib, time as _time
    raw = (user_text + "||" + assistant_text).encode("utf-8")
    h = hashlib.sha256(raw).hexdigest()[:16]
    key = "dialog_" + h

    hashes = _load_hashes()
    if key in hashes:
        return {"ok": True, "reason": "already indexed", "id": key}

    chunk_text = "[USER] " + user_text + "\\n[ASSISTANT] " + assistant_text
    meta = {
        "origin": "dialog",
        "source": "dialog",
        "date": _time.strftime("%Y-%m-%d"),
        "session_id": session_id,
        "role": "pair",
        "file_hash": h,
        "confidence": "high",
    }
    item = {"id": key, "text": chunk_text, "metadata": meta}
    added = chroma_store.add_batch([item])
    if added:
        hashes[key] = {
            "file": "dialog",
            "chunks": 1,
            "indexed_at": _time.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        _save_hashes(hashes)
    return {"ok": bool(added), "id": key}


'''

if "_index_dialog" not in src:
    src = src.replace(marker1, block + marker1, 1)

# === 2) vyzov v chat_one posle long_memory.append("assistant", ...) ===
marker2 = 'long_memory.append("assistant", answer, session_id="", tokens=r["completion_tokens"])'
if marker2 not in src:
    raise SystemExit("long_memory.append assistant anchor not found")

call_block = marker2 + '''

    # 28b: index dialog pair into Chroma
    try:
        _index_dialog(user_text, answer, session_id="")
    except Exception:
        pass'''

if "# 28b: index dialog pair into Chroma" not in src:
    src = src.replace(marker2, call_block, 1)

with io.open(p, "w", encoding="utf-8") as f:
    f.write(src)

print("patched_brain_28b OK")