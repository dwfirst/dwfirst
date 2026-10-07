# patch_orch3.py — переключить orchestrator с registry.py на module.py
import io, os, re

X = "X:" + os.sep
p = os.path.join(X, "07_router", "orchestrator.py")

with io.open(p, "r", encoding="utf-8-sig") as f:
    src = f.read()

# 1) заменить _get_tools
old_get = '''@lru_cache(maxsize=1)
def _get_tools():
    """Ленивая загрузка 08_tools/registry.py. Кэшируется на процесс."""
    path = os.path.join(TOOLS_DIR, "registry.py")
    spec = importlib.util.spec_from_file_location("iris_tools_registry", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod'''
new_get = '''@lru_cache(maxsize=1)
def _get_tools():
    """Ленивая загрузка 08_tools/module.py. Кэшируется на процесс."""
    path = os.path.join(TOOLS_DIR, "module.py")
    spec = importlib.util.spec_from_file_location("iris_tools", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod'''
if old_get not in src:
    raise SystemExit("old _get_tools not found")
src = src.replace(old_get, new_get, 1)

# 2) заменить ветку tool в _dispatch
old_tool = '''    if command == "tool":
        t = _get_tools()
        sub = kwargs.get("sub")
        args = kwargs.get("args") or []
        if not sub or sub == "list":
            return t.list_tools()
        if sub == "now":
            return t.call("now")
        if sub == "list_dir" and len(args) >= 1:
            return t.call("list_dir", path=args[0])
        if sub == "read_file" and len(args) >= 1:
            mc = int(args[1]) if len(args) >= 2 else 8000
            return t.call("read_file", path=args[0], max_chars=mc)
        if sub == "find_files" and len(args) >= 2:
            return t.call("find_files", pattern=args[0], root=args[1])
        return {"ok": False, "error": "bad tool args"}'''
new_tool = '''    if command == "tool":
        t = _get_tools()
        sub = kwargs.get("sub")
        args = kwargs.get("args") or []
        if not sub or sub == "list":
            names = sorted(getattr(t, "DISPATCH", {}).keys())
            return {"ok": True, "result": {"tools": names}}
        if sub == "now":
            return t.call("now")
        if sub == "list_dir" and len(args) >= 1:
            return t.call("list_dir", rel_path=args[0])
        if sub == "read_file" and len(args) >= 1:
            mb = int(args[1]) if len(args) >= 2 else 51200
            return t.call("read_file", rel_path=args[0], max_bytes=mb)
        if sub == "find_files" and len(args) >= 1:
            mr = int(args[1]) if len(args) >= 2 else 30
            return t.call("find_files", pattern=args[0], max_results=mr)
        return {"ok": False, "error": "bad tool args"}'''
if old_tool not in src:
    raise SystemExit("old tool branch not found")
src = src.replace(old_tool, new_tool, 1)

with io.open(p, "w", encoding="utf-8") as f:
    f.write(src)
print("patched_orch3 OK")