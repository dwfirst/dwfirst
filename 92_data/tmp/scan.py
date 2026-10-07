import os, sys
X = "X:" + os.sep

# 1) показать сигнатуру loader.load_model
print("=== loader.py (первые 80 строк) ===")
lp = os.path.join(X, "01_core", "modules", "loader.py")
with open(lp, "r", encoding="utf-8-sig") as f:
    for i, line in enumerate(f):
        if i >= 80: break
        print(line.rstrip())

print()
print("=== infer.py (первые 80 строк) ===")
ip = os.path.join(X, "01_core", "modules", "infer.py")
with open(ip, "r", encoding="utf-8-sig") as f:
    for i, line in enumerate(f):
        if i >= 80: break
        print(line.rstrip())

print()
print("=== поиск 'Ирис' в 11_roles ===")
root = os.path.join(X, "11_roles")
for cur, dirs, files in os.walk(root):
    for fn in sorted(files):
        if fn.lower().endswith(".md"):
            p = os.path.join(cur, fn)
            try:
                t = open(p, "r", encoding="utf-8-sig").read()
            except Exception as e:
                print("ERR", p, e); continue
            if "Ирис" in t:
                print(t.count("Ирис"), p)