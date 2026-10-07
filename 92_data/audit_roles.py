import os

X = "X:" + os.sep
roles_dir = os.path.join(X, "11_roles")

print("=== ROLE AUDIT ===")
for role in sorted(os.listdir(roles_dir)):
    rpath = os.path.join(roles_dir, role)
    if not os.path.isdir(rpath):
        continue
    files = {}
    for fname in ("prompt.md", "style.md", "rules.md", "examples.jsonl", "meta.json"):
        fp = os.path.join(rpath, fname)
        if os.path.exists(fp):
            size = os.path.getsize(fp)
            files[fname] = size
        else:
            files[fname] = None
    print(role)
    for k, v in files.items():
        mark = "OK" if v and v > 100 else ("empty" if v else "MISSING")
        print("   ", k.ljust(16), v, mark)
