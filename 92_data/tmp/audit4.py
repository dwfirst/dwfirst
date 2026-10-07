import os
X = "X:" + os.sep
out = os.path.join(X, "92_data", "tmp", "audit_junk_after.txt")
f = open(out, "w", encoding="utf-8")
cnt = 0
for r, dirs, files in os.walk(X):
    if "92_data" in r and "tmp" in r:
        continue
    for x in files:
        if x.endswith((".bak", ".bak2", ".bak3", ".pyc")) or ".bak_" in x:
            f.write(os.path.join(r, x) + "\n")
            cnt += 1
f.write("\nTOTAL: " + str(cnt) + "\n")
f.close()
print("junk after clean:", cnt)