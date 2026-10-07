# patch_parser_v3.py - tochnaya regulyarka + validaciya argumentov
import io, os

X = "X:" + os.sep
p = os.path.join(X, "08_tools", "parser.py")

with io.open(p, "r", encoding="utf-8-sig") as f:
    src = f.read()

# 1) zamena TOOL_RE na zhestkuyu versiyu
old_re = 'TOOL_RE = re.compile(r"\\[{1,2}\\s*TOOL\\s*:\\s*(.+?)\\s*\\]{1,2}", re.IGNORECASE)'
new_re = 'TOOL_RE = re.compile(r"\\[\\[?\\s*TOOL\\s*:\\s*(.+?)\\s*\\]\\]?", re.IGNORECASE)'
if old_re not in src:
    raise SystemExit("TOOL_RE anchor not found")
src = src.replace(old_re, new_re, 1)

# 2) TOOL_CALL_RE - to zhe
old_call_re = 'TOOL_CALL_RE = re.compile(r"\\[{1,2}\\s*TOOL_CALL\\s*:?\\s*\\]{1,2}\\s*([a-zA-Z_][a-zA-Z0-9_]*)\\s*\\(([^)]*)\\)", re.IGNORECASE)'
new_call_re = 'TOOL_CALL_RE = re.compile(r"\\[\\[?\\s*TOOL_CALL\\s*:?\\s*\\]\\]?\\s*([a-zA-Z_][a-zA-Z0-9_]*)\\s*\\(([^)]*)\\)", re.IGNORECASE)'
if old_call_re not in src:
    raise SystemExit("TOOL_CALL_RE anchor not found")
src = src.replace(old_call_re, new_call_re, 1)

# 3) _parse_args - belyy spisok znayutsya argumentov
old_args = '''def _parse_args(argstr):
    """Parse 'path=10_projects, pattern=meta' into dict.
    Also accepts space-separated 'path=... pattern=...'."""
    args = {}
    if not argstr:
        return args
    # сначала пробуем разбить по запятым, если их нет - по пробелам
    if "," in argstr:
        parts = [p.strip() for p in argstr.split(",") if p.strip()]
    else:
        parts = [p.strip() for p in argstr.split() if p.strip()]
    for p in parts:
        if "=" in p:
            k, v = p.split("=", 1)
            args[k.strip()] = v.strip().strip('"').strip("'")
        else:
            args.setdefault("_positional", []).append(p)
    return args'''

new_args = '''KNOWN_ARGS = {"path", "rel_path", "pattern", "max_bytes", "max_results"}

def _parse_args(argstr):
    """Parse 'path=10_projects, pattern=meta' into dict.
    Unknown args go to '_unknown' list, not silently dropped."""
    args = {}
    unknown = []
    if not argstr:
        return args
    if "," in argstr:
        parts = [p.strip() for p in argstr.split(",") if p.strip()]
    else:
        parts = [p.strip() for p in argstr.split() if p.strip()]
    for p in parts:
        if "=" in p:
            k, v = p.split("=", 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if k in KNOWN_ARGS:
                args[k] = v
            else:
                unknown.append(k + "=" + v)
        else:
            args.setdefault("_positional", []).append(p)
    if unknown:
        args["_unknown"] = unknown
    return args'''

if old_args not in src:
    raise SystemExit("_parse_args anchor not found")
src = src.replace(old_args, new_args, 1)

with io.open(p, "w", encoding="utf-8") as f:
    f.write(src)
print("patched_parser_v3 OK")