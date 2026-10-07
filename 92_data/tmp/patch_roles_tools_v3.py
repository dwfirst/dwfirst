# patch_roles_tools_v3.py - blok [INSTRUMENTY] s primerami formata
import io, os, shutil

X = "X:" + os.sep
ROLES = os.path.join(X, "11_roles")

# rol -> spisok instrumentov (dlya formatirovaniya primerov)
TOOLS_MAP = {
    "assistant":   ["now", "list_dir", "read_file", "find_files"],
    "archivist":   ["now", "list_dir", "read_file", "find_files"],
    "coder":       ["now", "list_dir", "read_file", "find_files"],
    "engineer":    ["now", "list_dir", "read_file", "find_files"],
    "philosopher": ["now", "read_file", "find_files"],
    "writer":      ["now", "read_file", "find_files"],
    "poet":        ["now"],
    "musician":    ["now"],
    "mirror":      ["now"],
}

# shablony primerov dlya kazhdogo instrumenta
EXAMPLES = {
    "now":       "[[TOOL: now]]",
    "list_dir":  "[[TOOL: list_dir, path=10_projects/books/book_iris]]",
    "read_file": "[[TOOL: read_file, path=10_projects/books/book_iris/context.md]]",
    "find_files":"[[TOOL: find_files, pattern=meta]]",
}

def build_block(tools):
    lines = ["[ИНСТРУМЕНТЫ]"]
    lines.append("Вызов — точно в таком формате:")
    for t in tools:
        lines.append("  " + EXAMPLES[t])
    if "list_dir" in tools or "read_file" in tools or "find_files" in tools:
        lines.append("Читать можно: 10_projects, 09_inbox, 03_memory_working, 92_data/exports.")
    return "\n".join(lines) + "\n"

for role, tools in TOOLS_MAP.items():
    p = os.path.join(ROLES, role, "prompt.md")
    if not os.path.exists(p):
        print("SKIP:", role)
        continue

    with io.open(p, "r", encoding="utf-8-sig") as f:
        txt = f.read()

    marker = "[ИНСТРУМЕНТЫ]"
    if marker in txt:
        idx = txt.find(marker)
        txt = txt[:idx].rstrip() + "\n"
    else:
        if not txt.endswith("\n"):
            txt += "\n"

    bak = p + ".bak3"
    if not os.path.exists(bak):
        shutil.copy2(p, bak)

    txt = txt + build_block(tools)

    with io.open(p, "w", encoding="utf-8") as f:
        f.write(txt)
    print("OK:", role)

print("done")