# patch_orch_setrole.py - chinit set_role i set_project
import io, os

X = "X:" + os.sep
p = os.path.join(X, "07_router", "orchestrator.py")

with io.open(p, "r", encoding="utf-8-sig") as f:
    src = f.read()

# 1) set_role
old_role = '''    if command == "set_role":
        state["role"]["active"] = kwargs.get("role")
        return state["role"]'''
new_role = '''    if command == "set_role":
        val = kwargs.get("role") or kwargs.get("sub")
        if val:
            state["role"]["active"] = val
        return state["role"]'''

if old_role not in src:
    raise SystemExit("set_role anchor not found")
src = src.replace(old_role, new_role, 1)

# 2) set_project
old_proj = '''    if command == "set_project":
        state["project"]["active"] = kwargs.get("project")
        return state["project"]'''
new_proj = '''    if command == "set_project":
        val = kwargs.get("project") or kwargs.get("sub")
        if val:
            state["project"]["active"] = val
        return state["project"]'''

if old_proj not in src:
    raise SystemExit("set_project anchor not found")
src = src.replace(old_proj, new_proj, 1)

with io.open(p, "w", encoding="utf-8") as f:
    f.write(src)
print("patched_setrole OK")