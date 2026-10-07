# patch_module_path.py - path= kak sinonim rel_path=, i validaciya argumentov
import io, os

X = "X:" + os.sep
p = os.path.join(X, "08_tools", "module.py")

with io.open(p, "r", encoding="utf-8-sig") as f:
    src = f.read()

# 1) list_dir: prinimaem path= ili rel_path=
old_ld = 'def list_dir(rel_path):\n    """List files in whitelisted dir (recursive, depth<=3)."""\n    abs_path = _safe_path(rel_path)'
new_ld = '''def list_dir(rel_path=None, path=None, **kwargs):
    """List files in whitelisted dir (recursive, depth<=3).
    Accepts rel_path= or path= as synonyms."""
    rel = rel_path or path
    if not rel:
        return {"ok": False, "error": "list_dir: missing 'path' argument"}
    if kwargs:
        return {"ok": False, "error": "list_dir: unknown args: " + ", ".join(kwargs.keys())}
    abs_path = _safe_path(rel)'''
if old_ld not in src:
    raise SystemExit("list_dir anchor not found")
src = src.replace(old_ld, new_ld, 1)

# 2) read_file
old_rf = 'def read_file(rel_path, max_bytes=MAX_READ_BYTES):\n    """Read whitelisted file (max 50KB). Returns text + meta."""\n    abs_path = _safe_path(rel_path)'
new_rf = '''def read_file(rel_path=None, path=None, max_bytes=MAX_READ_BYTES, **kwargs):
    """Read whitelisted file (max 50KB). Returns text + meta.
    Accepts rel_path= or path= as synonyms."""
    rel = rel_path or path
    if not rel:
        return {"ok": False, "error": "read_file: missing 'path' argument"}
    if kwargs:
        return {"ok": False, "error": "read_file: unknown args: " + ", ".join(kwargs.keys())}
    abs_path = _safe_path(rel)'''
if old_rf not in src:
    raise SystemExit("read_file anchor not found")
src = src.replace(old_rf, new_rf, 1)

# 3) find_files: prinimaem pattern=, maksimalno gibko
old_ff = 'def find_files(pattern, max_results=MAX_FIND_RESULTS):\n    """Find files by substring in name within whitelist."""\n    if not pattern:\n        return {"ok": False, "error": "empty pattern"}'
new_ff = '''def find_files(pattern=None, max_results=MAX_FIND_RESULTS, **kwargs):
    """Find files by substring in name within whitelist."""
    if kwargs:
        return {"ok": False, "error": "find_files: unknown args: " + ", ".join(kwargs.keys())}
    if not pattern:
        return {"ok": False, "error": "find_files: missing 'pattern' argument"}'''
if old_ff not in src:
    raise SystemExit("find_files anchor not found")
src = src.replace(old_ff, new_ff, 1)

with io.open(p, "w", encoding="utf-8") as f:
    f.write(src)
print("patched_module_path OK")