import os

X = "X:" + os.sep

print("=== ROOT ===")
for f in sorted(os.listdir(X)):
    fp = os.path.join(X, f)
    if os.path.isfile(fp):
        print("  FILE", f, os.path.getsize(fp))

print()
print("=== MODULES ===")
folders = [
    "01_core/modules",
    "02_memory_fast",
    "03_memory_working",
    "04_memory_long",
    "05_chroma",
    "06_reflection",
    "07_router",
    "08_tools",
    "09_inbox",
    "10_projects",
]
for folder in folders:
    fp = os.path.join(X, folder)
    if not os.path.isdir(fp):
        print(folder, "MISSING")
        continue
    print(folder + "/")
    for f in sorted(os.listdir(fp)):
        full = os.path.join(fp, f)
        if os.path.isfile(full):
            print("   ", f, os.path.getsize(full))
        elif os.path.isdir(full):
            print("   ", f + "/ (dir)")

print()
print("=== 00_dna ===")
dna = os.path.join(X, "00_dna")
for f in sorted(os.listdir(dna)):
    print("  ", f, os.path.getsize(os.path.join(dna, f)))

print()
print("=== identity_core check ===")
ic = os.path.join(X, "00_dna", "identity_core.md")
print("exists:", os.path.exists(ic))
if os.path.exists(ic):
    print("bytes:", os.path.getsize(ic))

print()
print("=== registry.py check ===")
reg = os.path.join(X, "08_tools", "registry.py")
print("exists:", os.path.exists(reg))
