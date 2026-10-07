"""module.py - safe tools for IRIS.

Read-only tools for the model: now, list_dir, read_file, find_files.
Strict whitelist. No write. No delete. No path escape.

API:
  now() -> dict
  list_dir(rel_path) -> dict
  read_file(rel_path, max_bytes=51200) -> dict
  find_files(pattern, max_results=30) -> dict
  call(name, **kwargs) -> dict  (dispatcher)
"""
import os
import re
import time

X = "X:" + os.sep

# Folders model is allowed to touch (relative to X:)
WHITELIST = [
    os.path.join("10_projects"),
    os.path.join("09_inbox"),
    os.path.join("03_memory_working"),
    os.path.join("92_data", "exports"),
]

MAX_READ_BYTES = 51200
MAX_LIST_DEPTH = 3
MAX_LIST_ITEMS = 200
MAX_FIND_RESULTS = 30


def _norm(rel):
    if not rel:
        return ""
    rel = rel.replace("/", os.sep).replace("\\", os.sep)
    return rel.lstrip(os.sep).strip()


def _safe_path(rel_path):
    """Return absolute path if inside whitelist, else None."""
    rel = _norm(rel_path)
    if not rel:
        return None
    abs_path = os.path.normpath(os.path.join(X, rel))
    # Must be under X:
    x_norm = os.path.normpath(X)
    if not abs_path.startswith(x_norm):
        return None
    # Must be under at least one whitelist dir
    for w in WHITELIST:
        w_abs = os.path.normpath(os.path.join(X, w))
        if abs_path == w_abs or abs_path.startswith(w_abs + os.sep):
            return abs_path
    return None


def now():
    """Current date and time."""
    t = time.localtime()
    return {
        "ok": True,
        "result": {
            "iso": time.strftime("%Y-%m-%dT%H:%M:%S", t),
            "date": time.strftime("%Y-%m-%d", t),
            "time": time.strftime("%H:%M:%S", t),
            "weekday": time.strftime("%A", t),
            "ts": round(time.time(), 3),
        },
    }


def list_dir(rel_path=None, path=None, **kwargs):
    """List files in whitelisted dir (recursive, depth<=3).
    Accepts rel_path= or path= as synonyms."""
    rel = rel_path or path
    if not rel:
        return {"ok": False, "error": "list_dir: missing 'path' argument"}
    if kwargs:
        return {"ok": False, "error": "list_dir: unknown args: " + ", ".join(kwargs.keys())}
    abs_path = _safe_path(rel)
    if abs_path is None:
        return {"ok": False, "error": "path not allowed or empty"}
    if not os.path.exists(abs_path):
        return {"ok": False, "error": "not found"}
    if not os.path.isdir(abs_path):
        return {"ok": False, "error": "not a directory"}

    items = []
    base_len = len(abs_path) + 1
    for root, dirs, files in os.walk(abs_path):
        rel_root = root[base_len:]
        depth = 0 if not rel_root else rel_root.count(os.sep) + 1
        if depth >= MAX_LIST_DEPTH:
            dirs[:] = []
        for d in sorted(dirs):
            items.append({"type": "dir", "path": os.path.join(rel_root, d) if rel_root else d})
        for f in sorted(files):
            full = os.path.join(root, f)
            try:
                size = os.path.getsize(full)
            except OSError:
                size = 0
            items.append({
                "type": "file",
                "path": os.path.join(rel_root, f) if rel_root else f,
                "bytes": size,
            })
        if len(items) > MAX_LIST_ITEMS:
            items = items[:MAX_LIST_ITEMS]
            break

    return {"ok": True, "result": {"path": rel, "count": len(items), "items": items}}


def read_file(rel_path=None, path=None, max_bytes=MAX_READ_BYTES, **kwargs):
    """Read whitelisted file (max 50KB). Returns text + meta.
    Accepts rel_path= or path= as synonyms."""
    rel = rel_path or path
    if not rel:
        return {"ok": False, "error": "read_file: missing 'path' argument"}
    if kwargs:
        return {"ok": False, "error": "read_file: unknown args: " + ", ".join(kwargs.keys())}
    abs_path = _safe_path(rel)
    if abs_path is None:
        return {"ok": False, "error": "path not allowed or empty"}
    if not os.path.exists(abs_path):
        return {"ok": False, "error": "not found"}
    if not os.path.isfile(abs_path):
        return {"ok": False, "error": "not a file"}

    try:
        size = os.path.getsize(abs_path)
    except OSError:
        return {"ok": False, "error": "stat failed"}

    truncated = False
    with open(abs_path, "r", encoding="utf-8-sig", errors="replace") as f:
        text = f.read(max_bytes)
    if size > max_bytes:
        truncated = True

    return {
        "ok": True,
        "result": {
            "path": rel,
            "bytes": size,
            "truncated": truncated,
            "text": text,
        },
    }


def find_files(pattern=None, max_results=MAX_FIND_RESULTS, **kwargs):
    """Find files by substring in name within whitelist."""
    if kwargs:
        return {"ok": False, "error": "find_files: unknown args: " + ", ".join(kwargs.keys())}
    if not pattern:
        return {"ok": False, "error": "find_files: missing 'pattern' argument"}
    pat = pattern.lower()
    out = []
    for w in WHITELIST:
        w_abs = os.path.join(X, w)
        if not os.path.isdir(w_abs):
            continue
        for root, dirs, files in os.walk(w_abs):
            for f in files:
                if pat in f.lower():
                    full = os.path.join(root, f)
                    rel = os.path.relpath(full, X)
                    out.append({
                        "path": rel,
                        "bytes": os.path.getsize(full) if os.path.exists(full) else 0,
                    })
                    if len(out) >= max_results:
                        return {"ok": True, "result": {"pattern": pattern, "count": len(out), "matches": out}}
    return {"ok": True, "result": {"pattern": pattern, "count": len(out), "matches": out}}


DISPATCH = {
    "now": now,
    "list_dir": list_dir,
    "read_file": read_file,
    "find_files": find_files,
}


def call(name, **kwargs):
    """Dispatcher. Returns result dict."""
    if name not in DISPATCH:
        return {"ok": False, "error": "unknown tool: " + str(name)}
    try:
        return DISPATCH[name](**kwargs)
    except Exception as e:
        return {"ok": False, "error": str(e)}


if __name__ == "__main__":
    print("tools module. whitelist:")
    for w in WHITELIST:
        print("  ", w)
    print("now:", now())
