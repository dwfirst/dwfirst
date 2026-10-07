import os
X = "X:" + os.sep
root = os.path.join(X, "11_roles")
pat = "Ирис"
for cur, dirs, files in os.walk(root):
    for fn in files:
        if fn.lower().endswith(".md"):
            p = os.path.join(cur, fn)
            try:
                t = open(p, "r", encoding="utf-8-sig").read()
            except Exception as e:
                print("ERR", p, e); continue
            if pat in t:
                cnt = t.count(pat)
                print(cnt, p)