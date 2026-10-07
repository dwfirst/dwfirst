# patch_orch2.py — добавляет 08_tools в sys.path внутри _get_tools
import io, os

X = "X:" + os.sep
p = os.path.join(X, "07_router", "orchestrator.py")

with io.open(p, "r", encoding="utf-8-sig") as f:
    src = f.read()

old = 'def _get_tools():\n    global _tools_registry\n    if _tools_registry is None:\n        import importlib.util as _iu\n        tp = os.path.join(X, "08_tools", "registry.py")'
new = 'def _get_tools():\n    global _tools_registry\n    if _tools_registry is None:\n        import importlib.util as _iu\n        td = os.path.join(X, "08_tools")\n        if td not in sys.path:\n            sys.path.insert(0, td)\n        tp = os.path.join(td, "registry.py")'

if old not in src:
    raise SystemExit("old _get_tools block not found")
src = src.replace(old, new, 1)

with io.open(p, "w", encoding="utf-8") as f:
    f.write(src)
print("patched2 OK")