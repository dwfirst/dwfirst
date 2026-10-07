import os
X = "X:" + os.sep
out = os.path.join(X, "92_data", "tmp", "audit_modules.txt")
f = open(out, "w", encoding="utf-8")
for d in ["01_core/modules", "02_memory_fast", "04_memory_long", "05_chroma", "08_tools", "09_inbox"]:
    f.write("=== " + d + " ===\n")
    full = os.path.join(X, d)
    if not os.path.isdir(full):
        f.write("  NOT FOUND\n")
        continue
    for x in sorted(os.listdir(full)):
        p = os.path.join(full, x)
        if os.path.isfile(p):
            f.write("  " + x + " (" + str(os.path.getsize(p)) + ")\n")
        else:
            f.write("  " + x + "/\n")
    f.write("\n")
f.close()
print("saved")