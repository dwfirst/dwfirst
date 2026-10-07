# patch_module_cosmetic.py - ispolzovat rel vmesto rel_path v returnah
import io, os

X = "X:" + os.sep
p = os.path.join(X, "08_tools", "module.py")

with io.open(p, "r", encoding="utf-8-sig") as f:
    src = f.read()

# list_dir: zamena 'path': rel_path na 'path': rel
old1 = 'return {"ok": True, "result": {"path": rel_path, "count": len(items), "items": items}}'
new1 = 'return {"ok": True, "result": {"path": rel, "count": len(items), "items": items}}'
if old1 not in src:
    raise SystemExit("list_dir return anchor not found")
src = src.replace(old1, new1, 1)

# read_file
old2 = '''    return {
        "ok": True,
        "result": {
            "path": rel_path,
            "bytes": size,
            "truncated": truncated,
            "text": text,
        },
    }'''
new2 = '''    return {
        "ok": True,
        "result": {
            "path": rel,
            "bytes": size,
            "truncated": truncated,
            "text": text,
        },
    }'''
if old2 not in src:
    raise SystemExit("read_file return anchor not found")
src = src.replace(old2, new2, 1)

with io.open(p, "w", encoding="utf-8") as f:
    f.write(src)
print("patched_module_cosmetic OK")