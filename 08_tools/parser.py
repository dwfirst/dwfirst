"""parser.py - parse tool tokens from model output.

Accepts both:
  [[TOOL: name, key=value, ...]]
  [TOOL: name, key=value, ...]

API:
  parse(text) -> {"clean_text": str, "calls": [{"name": str, "args": dict}]}
  strip(text) -> str
  has_tools(text) -> bool
"""
import re

# одна или две квадратных скобки с любой стороны
TOOL_RE = re.compile(r"\[\[?\s*TOOL\s*:\s*(.+?)\s*\]\]?", re.IGNORECASE)

# [TOOL_CALL]\nname(args) ili name(arg1, arg2=val)
TOOL_CALL_RE = re.compile(r"\[\[?\s*TOOL_CALL\s*:?\s*\]\]?\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\(([^)]*)\)", re.IGNORECASE)

KNOWN_ARGS = {"path", "rel_path", "pattern", "max_bytes", "max_results"}

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
    return args

def parse(text):
    """Find all tool tokens. Returns clean text + calls list."""
    if not text:
        return {"clean_text": "", "calls": []}

    calls = []
    for m in TOOL_RE.finditer(text):
        body = m.group(1).strip()
        if not body:
            continue
        # First token = tool name, rest = args
        if "," in body:
            name, rest = body.split(",", 1)
        elif " " in body:
            name, rest = body.split(" ", 1)
        else:
            name, rest = body, ""
        calls.append({
            "name": name.strip().lower(),
            "args": _parse_args(rest),
        })

    # dopolnitelno: [TOOL_CALL]\nname(args)
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
    clean_text = TOOL_CALL_RE.sub("", clean_text).strip()
    clean_text = re.sub(r"\n\s*\n\s*\n+", "\n\n", clean_text).strip()

    return {"clean_text": clean_text, "calls": calls}

def strip(text):
    if not text:
        return ""
    return TOOL_RE.sub("", text).strip()

def has_tools(text):
    return bool(text and TOOL_RE.search(text))

if __name__ == "__main__":
    tests = [
        "Hello. [[TOOL: now]] done.",
        "Hello. [TOOL: now] done.",
        "Let me check. [[TOOL: list_dir, path=10_projects]]",
        "Let me check. [TOOL: list_dir, path=10_projects]",
        "Let me check. [TOOL:list_dir path=10_projects]",
        "Reading. [[TOOL: read_file, path=10_projects/books/book_iris/context.md]]",
        "Searching [[TOOL: find_files, pattern=meta]] end.",
        "Searching [TOOL: find_files pattern=meta] end.",
    ]
    for t in tests:
        print("INPUT:", t)
        print("  ", parse(t))