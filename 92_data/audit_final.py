import os
import json

X = "X:" + os.sep

print("=== CONFIG ===")
cfg = os.path.join(X, "00_dna", "config.json")
if os.path.exists(cfg):
    with open(cfg, "r", encoding="utf-8-sig") as f:
        c = json.load(f)
    print(json.dumps(c, ensure_ascii=False, indent=2))
else:
    print("MISSING")

print()
print("=== identity_core.md ===")
ic = os.path.join(X, "00_dna", "identity_core.md")
print("exists:", os.path.exists(ic), "bytes:", os.path.getsize(ic) if os.path.exists(ic) else 0)

print()
print("=== brain.py check ===")
bp = os.path.join(X, "01_core", "modules", "brain.py")
if os.path.exists(bp):
    with open(bp, "r", encoding="utf-8-sig") as f:
        t = f.read()
    print("bytes:", os.path.getsize(bp))
    print("has 'split=True':", "split=" in t)
    print("has '_load_budget':", "_load_budget" in t)
    print("has 'core':", '"core"' in t or "'core'" in t)
    print("has 'iris_router':", "iris_router" in t)
    print("has 'iris_tools':", "iris_tools" in t)
    print("has '_index_dialog':", "_index_dialog" in t)

print()
print("=== 08_tools ===")
for f in ["module.py", "parser.py"]:
    fp = os.path.join(X, "08_tools", f)
    print(f, "->", os.path.getsize(fp) if os.path.exists(fp) else "MISSING")

print()
print("=== STATE FILES ===")
for f in ["project_state.md", "ver_0.1.txt", "project_state.md_2.md", "project_state_v2_draft.md"]:
    fp = os.path.join(X, f)
    if os.path.exists(fp):
        with open(fp, "r", encoding="utf-8-sig") as fh:
            first = fh.readline().strip()
        print(f, os.path.getsize(fp), "| first line:", first[:80])
    else:
        print(f, "MISSING")
