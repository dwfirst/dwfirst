import os
X = "X:" + os.sep

removed = []

# 1) vse .bak_* vo vseh papkah
for r, dirs, files in os.walk(X):
    if "92_data" in r and "tmp" in r:
        continue
    for x in files:
        if ".bak_" in x:
            p = os.path.join(r, x)
            try:
                os.remove(p)
                removed.append(p)
            except Exception as e:
                print("ERR:", p, e)

# 2) .bak2 i .bak3 v rolях
for r in sorted(os.listdir(os.path.join(X, "11_roles"))):
    d = os.path.join(X, "11_roles", r)
    if not os.path.isdir(d):
        continue
    for x in [".bak2", ".bak3"]:
        p = os.path.join(d, "prompt.md" + x)
        if os.path.exists(p):
            try:
                os.remove(p)
                removed.append(p)
            except Exception as e:
                print("ERR:", p, e)

print("REMOVED:", len(removed))
for p in removed:
    print("  ", p)