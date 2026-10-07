# patch_orch.py — добавляет команду tool в orchestrator.py
import io, os, re

X = "X:" + os.sep
p = os.path.join(X, "07_router", "orchestrator.py")

with io.open(p, "r", encoding="utf-8-sig") as f:
    src = f.read()

# 1) добавить импорт registry через importlib (без sys.path хаков)
if "import _tools_registry" not in src:
    anchor = "X = \"X:\" + os.sep\n"
    inject = anchor + "\n_tools_registry = None\n\ndef _get_tools():\n    global _tools_registry\n    if _tools_registry is None:\n        import importlib.util as _iu\n        tp = os.path.join(X, \"08_tools\", \"registry.py\")\n        spec = _iu.spec_from_file_location(\"iris_tools_registry\", tp)\n        m = _iu.module_from_spec(spec)\n        spec.loader.exec_module(m)\n        _tools_registry = m\n    return _tools_registry\n"
    if anchor in src:
        src = src.replace(anchor, inject, 1)
    else:
        raise SystemExit("anchor X= not found")

# 2) вставить ветку tool перед raise ValueError
if 'if command == "tool":' not in src:
    marker = '    raise ValueError("Неизвестная команда: " + command)'
    branch = (
        '    if command == "tool":\n'
        '        t = _get_tools()\n'
        '        sub = kwargs.get("sub")\n'
        '        args = kwargs.get("args") or []\n'
        '        if not sub or sub == "list":\n'
        '            return t.list_tools()\n'
        '        if sub == "now":\n'
        '            return t.call("now")\n'
        '        if sub == "list_dir" and len(args) >= 1:\n'
        '            return t.call("list_dir", path=args[0])\n'
        '        if sub == "read_file" and len(args) >= 1:\n'
        '            mc = int(args[1]) if len(args) >= 2 else 8000\n'
        '            return t.call("read_file", path=args[0], max_chars=mc)\n'
        '        if sub == "find_files" and len(args) >= 2:\n'
        '            return t.call("find_files", pattern=args[0], root=args[1])\n'
        '        return {"ok": False, "error": "bad tool args"}\n'
    )
    if marker not in src:
        raise SystemExit("marker raise ValueError not found")
    src = src.replace(marker, branch + marker, 1)

# 3) проброс args в __main__
old_main = 'cmd = sys.argv[1] if len(sys.argv) > 1 else "state"\n    print(json.dumps(run(cmd), ensure_ascii=False, indent=2))'
new_main = (
    'cmd = sys.argv[1] if len(sys.argv) > 1 else "state"\n'
    '    sub = sys.argv[2] if len(sys.argv) > 2 else None\n'
    '    extra = sys.argv[3:] if len(sys.argv) > 3 else []\n'
    '    print(json.dumps(run(cmd, sub=sub, args=extra), ensure_ascii=False, indent=2))'
)
if "sub = sys.argv[2]" not in src:
    if old_main not in src:
        raise SystemExit("main block not found")
    src = src.replace(old_main, new_main, 1)

with io.open(p, "w", encoding="utf-8") as f:
    f.write(src)

print("patched OK")