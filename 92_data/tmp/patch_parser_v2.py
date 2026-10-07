# patch_parser_v2.py - dobavlyaem poisk [TOOL_CALL] formata
import io, os

X = "X:" + os.sep
p = os.path.join(X, "08_tools", "parser.py")

with io.open(p, "r", encoding="utf-8-sig") as f:
    src = f.read()

# 1) dobavit vtoruyu regulyarku posle TOOL_RE
old_re = 'TOOL_RE = re.compile(r"\\[{1,2}\\s*TOOL\\s*:\\s*(.+?)\\s*\\]{1,2}", re.IGNORECASE)'
new_re = old_re + '\n\n# [TOOL_CALL]\\nname(args) ili name(arg1, arg2=val)\nTOOL_CALL_RE = re.compile(r"\\[{1,2}\\s*TOOL_CALL\\s*:?\\s*\\]{1,2}\\s*([a-zA-Z_][a-zA-Z0-9_]*)\\s*\\(([^)]*)\\)", re.IGNORECASE)'

if old_re not in src:
    raise SystemExit("regex anchor not found")
if "TOOL_CALL_RE" not in src:
    src = src.replace(old_re, new_re, 1)

# 2) dobavit obrabotku v parse() pered TOOL_RE.sub
old_parse_end = '    clean_text = TOOL_RE.sub("", text).strip()'
new_parse_end = '''    # dopolnitelno: [TOOL_CALL]\\nname(args)
    for m in TOOL_CALL_RE.finditer(text):
        name = m.group(1).strip().lower()
        argstr = m.group(2).strip()
        args = {}
        if argstr:
            # "path=10_projects/books/book_iris" ili "10_projects/books/book_iris"
            if "=" in argstr:
                for part in argstr.split(","):
                    if "=" in part:
                        k, v = part.split("=", 1)
                        args[k.strip()] = v.strip().strip('"').strip("'")
            else:
                args["path"] = argstr.strip().strip('"').strip("'")
        calls.append({"name": name, "args": args})

    clean_text = TOOL_RE.sub("", text).strip()
    clean_text = TOOL_CALL_RE.sub("", clean_text).strip()'''

if old_parse_end not in src:
    raise SystemExit("parse end anchor not found")
src = src.replace(old_parse_end, new_parse_end, 1)

with io.open(p, "w", encoding="utf-8") as f:
    f.write(src)
print("patched_parser_v2 OK")