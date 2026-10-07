"""indexer.py - scan projects, build meta.json and _index.json.

No model. Pure filesystem scan. Fast.

API:
  scan_project(proj_rel) -> dict
  scan_all() -> list of dict
  update_project_meta(proj_rel) -> dict
  update_all() -> list
"""
import os
import json
import time

X = "X:" + os.sep
PROJECTS = os.path.join(X, "10_projects")
INDEX_FILE = os.path.join(PROJECTS, "_index.json")


def _project_path(proj_rel):
    return os.path.join(PROJECTS, *proj_rel.split("/"))


def _ts_to_iso(ts):
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(ts))


def _scan_dir(base):
    """Walk project dir, collect files and dirs structure."""
    files = []
    dirs = {}
    for root, subdirs, filenames in os.walk(base):
        subdirs.sort()
        filenames.sort()
        rel_root = os.path.relpath(root, base).replace("\\", "/")
        if rel_root == ".":
            rel_root = ""
        for f in filenames:
            full = os.path.join(root, f)
            rel = (rel_root + "/" + f) if rel_root else f
            try:
                st = os.stat(full)
                files.append({
                    "path": rel,
                    "bytes": st.st_size,
                    "modified": _ts_to_iso(st.st_mtime),
                })
            except OSError:
                continue
        for d in subdirs:
            rel = (rel_root + "/" + d) if rel_root else d
            full_d = os.path.join(root, d)
            count = sum(len(fs) for _, _, fs in os.walk(full_d))
            dirs[rel] = count
    return files, dirs


def scan_project(proj_rel):
    """Scan one project. Returns meta dict (does not write)."""
    base = _project_path(proj_rel)
    if not os.path.isdir(base):
        return None

    st = os.stat(base)
    files, dirs = _scan_dir(base)

    # summary counters
    total_bytes = sum(f["bytes"] for f in files)
    last_modified = max((f["modified"] for f in files), default=_ts_to_iso(st.st_mtime))

    cat, name = proj_rel.split("/", 1) if "/" in proj_rel else ("", proj_rel)

    meta = {
        "id": proj_rel,
        "category": cat,
        "name": name,
        "path": base,
        "created": _ts_to_iso(st.st_ctime),
        "modified": last_modified,
        "scanned_at": _ts_to_iso(time.time()),
        "file_count": len(files),
        "dir_count": len(dirs),
        "total_bytes": total_bytes,
        "files": files,
        "dirs": dirs,
        "summary": "",
        "tags": [],
    }
    return meta


def scan_all():
    """Scan all projects. Returns list of meta dicts."""
    if not os.path.isdir(PROJECTS):
        return []
    out = []
    for cat in sorted(os.listdir(PROJECTS)):
        cat_path = os.path.join(PROJECTS, cat)
        if not os.path.isdir(cat_path) or cat.startswith("_"):
            continue
        for proj in sorted(os.listdir(cat_path)):
            proj_path = os.path.join(cat_path, proj)
            if os.path.isdir(proj_path):
                rel = cat + "/" + proj
                meta = scan_project(rel)
                if meta:
                    out.append(meta)
    return out


def update_project_meta(proj_rel):
    """Scan one project and write its meta.json (merge with existing tags/summary)."""
    meta = scan_project(proj_rel)
    if not meta:
        return None

    meta_file = os.path.join(_project_path(proj_rel), "meta.json")
    # Preserve summary and tags if they exist
    if os.path.exists(meta_file):
        try:
            with open(meta_file, "r", encoding="utf-8-sig") as f:
                old = json.load(f)
            if old.get("summary"):
                meta["summary"] = old["summary"]
            if old.get("tags"):
                meta["tags"] = old["tags"]
        except Exception:
            pass

    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    return meta


def update_all():
    """Update meta.json for all projects + rewrite _index.json."""
    metas = scan_all()
    for m in metas:
        update_project_meta(m["id"])

    index = {
        "updated_at": _ts_to_iso(time.time()),
        "total_projects": len(metas),
        "projects": [
            {
                "id": m["id"],
                "category": m["category"],
                "name": m["name"],
                "created": m["created"],
                "modified": m["modified"],
                "file_count": m["file_count"],
                "total_bytes": m["total_bytes"],
                "summary": m["summary"],
                "tags": m["tags"],
            }
            for m in metas
        ],
    }
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    return metas


if __name__ == "__main__":
    metas = update_all()
    print("[indexer] updated", len(metas), "projects")
    for m in metas:
        print(" -", m["id"], "|", m["file_count"], "files |", round(m["total_bytes"]/1024, 1), "KB")
