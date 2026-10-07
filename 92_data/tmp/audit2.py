import os
X = "X:" + os.sep
out = os.path.join(X, "92_data", "tmp", "audit_roles.txt")
f = open(out, "w", encoding="utf-8")
d = os.path.join(X, "11_roles")
for r in sorted(os.listdir(d)):
    full = os.path.join(d, r)
    if not os.path.isdir(full):
        continue
    f.write("=== " + r + " ===\n")
    for x in sorted(os.listdir(full)):
        p = os.path.join(full, x)
        if os.path.isfile(p):
            f.write("  " + x + " (" + str(os.path.getsize(p)) + ")\n")
        else:
            f.write("  " + x + "/\n")
    f.write("\n")
f.close()
print("saved")