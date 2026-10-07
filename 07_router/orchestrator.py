"""
IRIS Orchestrator — единая точка входа.
"""
import json
import os
import sys
import importlib
import importlib.util
from datetime import datetime
from functools import lru_cache

X = "X:" + os.sep
STATE_FILE = os.path.join(X, "07_router", "state.json")
TOOLS_DIR = os.path.join(X, "08_tools")

MODULES = {
    "core":       os.path.join(X, "01_core", "modules", "module.py"),
    "mem_fast":   os.path.join(X, "02_memory_fast", "module.py"),
    "mem_work":   os.path.join(X, "03_memory_working", "module.py"),
    "mem_long":   os.path.join(X, "04_memory_long", "module.py"),
    "chroma":     os.path.join(X, "05_chroma", "module.py"),
    "reflection": os.path.join(X, "06_reflection", "module.py"),
    "tools":      os.path.join(X, "08_tools", "module.py"),
    "inbox":      os.path.join(X, "09_inbox", "module.py"),
    "projects":   os.path.join(X, "10_projects", "module.py"),
    "roles":      os.path.join(X, "11_roles", "module.py"),
}

@lru_cache(maxsize=1)
def _get_tools():
    """Ленивая загрузка 08_tools/module.py. Кэшируется на процесс."""
    path = os.path.join(TOOLS_DIR, "module.py")
    spec = importlib.util.spec_from_file_location("iris_tools", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    return default_state()

def default_state():
    return {
        "model": {"loaded": False, "name": None, "threads": 2},
        "role": {"active": None},
        "project": {"active": None},
        "session": {"id": None, "started": None},
        "last_command": None,
        "last_error": None,
    }

def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def _load_module(name):
    path = MODULES.get(name)
    if not path or not os.path.exists(path):
        return None
    spec = importlib.util.spec_from_file_location("iris_mod_" + name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def run(command, **kwargs):
    state = load_state()
    state["last_command"] = {"name": command, "at": datetime.now().isoformat()}
    try:
        result = _dispatch(command, state, **kwargs)
        state["last_error"] = None
        save_state(state)
        return {"ok": True, "result": result}
    except Exception as e:
        state["last_error"] = {"command": command, "error": str(e)}
        save_state(state)
        return {"ok": False, "error": str(e)}

def _dispatch(command, state, **kwargs):
    if command == "ping":
        return "pong"
    if command == "state":
        return state
    if command == "module_info":
        mod = _load_module(kwargs.get("name"))
        if not mod:
            return {"exists": False}
        return {"exists": True, "info": mod.info() if hasattr(mod, "info") else "no info()"}
    if command == "modules_status":
        out = {}
        for name, path in MODULES.items():
            out[name] = {"path": path, "exists": os.path.exists(path)}
        return out
    if command == "switch_model":
        return {"todo": "switch_model", "args": kwargs}
    if command == "set_threads":
        state["model"]["threads"] = int(kwargs.get("n", 2))
        return state["model"]
    if command == "reload_model":
        return {"todo": "reload_model"}
    if command == "set_role":
        val = kwargs.get("role") or kwargs.get("sub")
        if val:
            state["role"]["active"] = val
        return state["role"]
    if command == "set_project":
        val = kwargs.get("project") or kwargs.get("sub")
        if val:
            state["project"]["active"] = val
        return state["project"]
    if command == "clear_session":
        return {"todo": "clear_session"}
    if command == "clear_working":
        return {"todo": "clear_working"}
    if command == "clear_long":
        return {"todo": "clear_long"}
    if command == "rebuild_chroma":
        return {"todo": "rebuild_chroma"}
    if command == "run_reflection":
        return {"todo": "run_reflection"}
    if command == "tool":
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
        return {"ok": False, "error": "bad tool args"}
    raise ValueError("Неизвестная команда: " + command)

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "state"
    sub = sys.argv[2] if len(sys.argv) > 2 else None
    extra = sys.argv[3:] if len(sys.argv) > 3 else []
    print(json.dumps(run(cmd, sub=sub, args=extra), ensure_ascii=False, indent=2))