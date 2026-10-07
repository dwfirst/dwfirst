# patch_roles_tools_v2.py - zamena bloka [INSTRUMENTY] vo vseh rolyah
import io, os, shutil

X = "X:" + os.sep
ROLES = os.path.join(X, "11_roles")

# rol -> (spisok instrumentov, polnyy blok)
FULL_ACCESS = "10_projects, 09_inbox, 03_memory_working, 92_data/exports."

TOOLS_MAP = {
    "assistant":   ("now, list_dir, read_file, find_files", FULL_ACCESS, True),
    "archivist":   ("now, list_dir, read_file, find_files", FULL_ACCESS, True),
    "coder":       ("now, list_dir, read_file, find_files", FULL_ACCESS, True),
    "engineer":    ("now, list_dir, read_file, find_files", FULL_ACCESS, True),
    "philosopher": ("now, read_file, find_files", FULL_ACCESS, False),
    "writer":      ("now, read_file, find_files", FULL_ACCESS, False),
    "poet":        ("now", None, False),
    "musician":    ("now", None, False),
    "mirror":      ("now", None, False),
}

def build_block(tools, access, full):
    lines = ["[ИНСТРУМЕНТЫ]"]
    lines.append("Доступно: " + tools + ".")
    if tools == "now":
        lines.append("Формат: [[TOOL: now]]")
    else:
        lines.append("Формат: [[TOOL: name, key=value]]")
    if access:
        lines.append("Читать можно: " + access)
    if full:
        lines.append("Когда нужно узнать время, файл, папку — зови инструмент.")
    return "\n".join(lines) + "\n"

for role, (tools, access, full) in TOOLS_MAP.items():
    p = os.path.join(ROLES, role, "prompt.md")
    if not os.path.exists(p):
        print("SKIP (not found):", role)
        continue

    with io.open(p, "r", encoding="utf-8-sig") as f:
        txt = f.read()

    # nayti i udalit staryy blok [INSTRUMENTY], esli est
    marker = "[ИНСТРУМЕНТЫ]"
    if marker in txt:
        idx = txt.find(marker)
        txt = txt[:idx].rstrip() + "\n"
    else:
        if not txt.endswith("\n"):
            txt += "\n"

    # backup (tolko pervyy raz)
    bak = p + ".bak2"
    if not os.path.exists(bak):
        shutil.copy2(p, bak)

    new_block = build_block(tools, access, full)
    txt = txt + new_block

    with io.open(p, "w", encoding="utf-8") as f:
        f.write(txt)
    print("OK:", role)

print("done")