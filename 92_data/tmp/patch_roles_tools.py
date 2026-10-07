# patch_roles_tools.py - dobavlyaem [INSTRUMENTY] v kazhduyu rol'
import io, os, shutil

X = "X:" + os.sep
ROLES = os.path.join(X, "11_roles")

# karta: rol -> spisok instrumentov
TOOLS_MAP = {
    "assistant":   "now, list_dir, read_file, find_files",
    "archivist":   "now, list_dir, read_file, find_files",
    "coder":       "now, list_dir, read_file, find_files",
    "engineer":    "now, list_dir, read_file, find_files",
    "mirror":      "now",
    "musician":    "now",
    "philosopher": "now, read_file, find_files",
    "poet":        "now",
    "writer":      "now, read_file, find_files",
}

for role, tools in TOOLS_MAP.items():
    p = os.path.join(ROLES, role, "prompt.md")
    if not os.path.exists(p):
        print("SKIP (not found):", role)
        continue

    with io.open(p, "r", encoding="utf-8-sig") as f:
        txt = f.read()

    if "[ИНСТРУМЕНТЫ]" in txt:
        print("SKIP (already has):", role)
        continue

    # backup
    shutil.copy2(p, p + ".bak")

    # dobavlyaem blok v konec
    if not txt.endswith("\n"):
        txt += "\n"
    txt += "[ИНСТРУМЕНТЫ]\n" + tools + ".\n"

    with io.open(p, "w", encoding="utf-8") as f:
        f.write(txt)
    print("OK:", role, "->", tools)

print("done")