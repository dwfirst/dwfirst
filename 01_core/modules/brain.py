"""
brain.py - high-level IRIS brain with persistent memory.

Loads model once, keeps session.log + window.jsonl, applies sliding compaction.
UI calls chat_one(user_text) - history lives on disk, not in UI.
"""
import os
import sys

X = "X:" + os.sep
MODULES = os.path.join(X, "01_core", "modules")
MEM_FAST = os.path.join(X, "02_memory_fast")
for p in (MODULES, MEM_FAST):
    if p not in sys.path:
        sys.path.insert(0, p)

from loader import load_model
from infer import generate, count_messages_tokens
import storage
import counter
import compaction

# vector store
CHROMA_DIR = os.path.join(X, "05_chroma")
if CHROMA_DIR not in sys.path:
    sys.path.insert(0, CHROMA_DIR)
try:
    import chroma_store
except Exception:
    chroma_store = None

# router (auto role/project/retrieval)
ROUTER_DIR = os.path.join(X, "07_router")
if ROUTER_DIR not in sys.path:
    sys.path.insert(0, ROUTER_DIR)
try:
    import router as iris_router
except Exception:
    iris_router = None

# tools
TOOLS_DIR = os.path.join(X, "08_tools")
if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)
try:
    import module as iris_tools
    import parser as iris_parser
except Exception:
    iris_tools = None
    iris_parser = None

# long-term archive (append-only, never deleted)
LONG = os.path.join(X, "04_memory_long")
if LONG not in sys.path:
    sys.path.insert(0, LONG)
import long_memory

_LLAMA = None
_META = None


def get_llama(verbose=False):
    global _LLAMA, _META
    if _LLAMA is None:
        _LLAMA, _META = load_model(verbose=verbose)
    return _LLAMA, _META


def reset():
    """Выгрузить модель из RAM немедленно."""
    global _LLAMA, _META
    if _LLAMA is not None:
        try:
            _LLAMA.close()
        except Exception:
            pass
    _LLAMA = None
    _META = None
    import gc
    gc.collect()


def _to_chat(window):
    """Convert window records to chat format."""
    return [{"role": m["role"], "content": m["content"]} for m in window]


def _normalize_roles(msgs):
    """Remove consecutive identical roles (except system)."""
    out = []
    last = None
    for m in msgs:
        r = m.get("role")
        if r == "system":
            out.append(m)
            continue
        if r == last:
            continue
        out.append(m)
        last = r
    return out



# ---------- context assembly (role + project) ----------

ROLES_DIR = os.path.join(X, "11_roles")
PROJECTS_DIR = os.path.join(X, "10_projects")
STATE_FILE = os.path.join(X, "07_router", "state.json")


def _read_state():
    """Read runtime state.json. Returns dict or empty."""
    if not os.path.exists(STATE_FILE):
        return {}
    try:
        import json as _json
        with open(STATE_FILE, "r", encoding="utf-8-sig") as f:
            return _json.load(f)
    except Exception:
        return {}


def _read_file_safe(path):
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8-sig") as f:
        return f.read().strip()



def _clean_role_file(text, min_chars=80):
    """Drop empty bullet lines like '- Тон:' and return cleaned text or '' if too short."""
    if not text:
        return ""
    lines = []
    for raw in text.split("\n"):
        s = raw.rstrip()
        stripped = s.strip()
        if not stripped:
            continue
        # Drop bullet with empty value: "- Something:"
        if stripped.startswith("-") and stripped.endswith(":"):
            continue
        # Drop bullet where value after colon is empty or too short (<=2 chars)
        if stripped.startswith("-") and ":" in stripped:
            val = stripped.split(":", 1)[1].strip()
            if len(val) <= 2:
                continue
        lines.append(s)
    cleaned = "\n".join(lines).strip()
    if len(cleaned) < min_chars:
        return ""
    return cleaned




def _retrieve(llama, query, top_k=5, max_tokens=1500, origin_filter=None):
    """Search Chroma for relevant chunks, cap by tokens. Returns (text_block, info)."""
    if chroma_store is None or not query:
        return "", {"count": 0, "tokens": 0, "candidates": 0}

    try:
        results = chroma_store.search(query, top_k=top_k, origin_filter=origin_filter)
    except Exception as e:
        return "", {"error": str(e)}

    if not results or "error" in (results[0] if results else {}):
        return "", {"count": 0, "tokens": 0, "candidates": 0}

    lines = ["[ВОСПОМИНАНИЯ ИЗ АРХИВА]"]
    used_tokens = 0
    added = 0
    for r in results:
        text = r.get("text", "").strip()
        if not text:
            continue
        meta = r.get("metadata") or {}
        src = meta.get("source", "?")
        dist = round(r.get("distance", 0.0), 3)
        chunk = "\n[" + str(added + 1) + "] " + src + " / dist " + str(dist) + "\n" + text
        chunk_tokens = counter.count_text(llama, chunk)
        if used_tokens + chunk_tokens > max_tokens and added > 0:
            break
        lines.append(chunk)
        used_tokens += chunk_tokens
        added += 1

    if added == 0:
        return "", {"count": 0, "tokens": 0, "candidates": len(results)}

    block = "\n".join(lines)
    return block, {"count": added, "tokens": used_tokens, "candidates": len(results)}


def _load_budget():
    """Read budget section from config.json."""
    cfg_path = os.path.join(X, "00_dna", "config.json")
    defaults = {"core": 400, "role": 400, "project": 400,
                "retrieval": 1800, "window": 4500,
                "query": 600, "reserve": 700}
    if not os.path.exists(cfg_path):
        return defaults
    try:
        import json as _json
        with open(cfg_path, "r", encoding="utf-8-sig") as f:
            cfg = _json.load(f)
        b = cfg.get("budget", {})
        return {
            "core":      b.get("core", defaults["core"]),
            "role":      b.get("role", defaults["role"]),
            "project":   b.get("project", defaults["project"]),
            "retrieval": b.get("retrieval", defaults["retrieval"]),
            "window":    b.get("window", defaults["window"]),
            "query":     b.get("query", defaults["query"]),
            "reserve":   b.get("reserve", defaults["reserve"]),
        }
    except Exception:
        return defaults


def _truncate_text(llama, text, max_tokens):
    """Truncate text to fit max_tokens. Keeps beginning."""
    if not text:
        return text, 0
    ids = llama.tokenize(text.encode("utf-8"))
    if len(ids) <= max_tokens:
        return text, len(ids)
    ids = ids[:max_tokens]
    truncated = llama.detokenize(ids).decode("utf-8", errors="ignore")
    return truncated, max_tokens




def _project_card(cat, name):
    """Build a short project card from meta.json. Returns str or ''."""
    import json as _json
    meta_file = os.path.join(PROJECTS_DIR, cat, name, "meta.json")
    if not os.path.exists(meta_file):
        return ""
    try:
        with open(meta_file, "r", encoding="utf-8-sig") as f:
            m = _json.load(f)
    except Exception:
        return ""

    files = m.get("files", [])
    dirs = m.get("dirs", {})
    modified = m.get("modified", "?")

    lines = []
    # dirs with count
    dir_parts = []
    for d, cnt in dirs.items():
        dir_parts.append(d + "/ (" + str(cnt) + ")")
    if dir_parts:
        lines.append("Папки: " + ", ".join(sorted(dir_parts)))

    # files (max 10)
    file_parts = []
    for f in files[:10]:
        file_parts.append(f.get("path", "?"))
    if file_parts:
        lines.append("Файлы: " + ", ".join(file_parts))
    if len(files) > 10:
        lines.append("... ещё " + str(len(files) - 10) + " файлов")

    if modified:
        lines.append("Изменён: " + str(modified)[:16])

    return "\n".join(lines)

def build_system_message(role_override=None, split=False):
    """Build system message from core identity only.
    role_override is accepted for backward compat but ignored.
    split=True: returns {"core": str, "role": "", "project": ""}.
    split=False: returns core string."""
    out = {"core": "", "role": "", "project": ""}

    core_path = os.path.join(X, "00_dna", "identity_core.md")
    core_raw = _read_file_safe(core_path)
    if core_raw:
        cleaned = _clean_role_file(core_raw, min_chars=50)
        out["core"] = cleaned or core_raw

    if split:
        return out
    return out["core"]

def _load_hashes():
    """Load ingested_hashes.json from Chroma."""
    import json as _json
    path = os.path.join(X, "05_chroma", "ingested_hashes.json")
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            return _json.load(f)
    except Exception:
        return {}


def _save_hashes(hashes):
    """Save ingested_hashes.json."""
    import json as _json
    path = os.path.join(X, "05_chroma", "ingested_hashes.json")
    with open(path, "w", encoding="utf-8") as f:
        _json.dump(hashes, f, ensure_ascii=False, indent=2)


def _index_dialog(user_text, assistant_text, session_id=""):
    """Index a user+assistant pair into Chroma. Idempotent. Skips tests."""
    if chroma_store is None:
        return {"ok": False, "reason": "no chroma"}
    if not user_text or not assistant_text:
        return {"ok": False, "reason": "empty"}
    if session_id.startswith("test_"):
        return {"ok": False, "reason": "test session skipped"}

    import hashlib, time as _time
    raw = (user_text + "||" + assistant_text).encode("utf-8")
    h = hashlib.sha256(raw).hexdigest()[:16]
    key = "dialog_" + h

    hashes = _load_hashes()
    if key in hashes:
        return {"ok": True, "reason": "already indexed", "id": key}

    chunk_text = "[USER] " + user_text + "\n[ASSISTANT] " + assistant_text
    meta = {
        "origin": "dialog",
        "source": "dialog",
        "date": _time.strftime("%Y-%m-%d"),
        "session_id": session_id,
        "role": "pair",
        "file_hash": h,
        "confidence": "high",
    }
    item = {"id": key, "text": chunk_text, "metadata": meta}
    added = chroma_store.add_batch([item])
    if added:
        hashes[key] = {
            "file": "dialog",
            "chunks": 1,
            "indexed_at": _time.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        _save_hashes(hashes)
    return {"ok": bool(added), "id": key}


def chat_one(user_text, max_tokens=1024, temperature=0.7, top_p=0.9,
             auto_compact=True):
    """
    One turn: append user, maybe compact, generate, append assistant.
    Returns dict with text, tps, compaction info.
    """
    llama, _ = get_llama()

    # 1. Append user to session.log (originals)
    user_tokens = counter.count_text(llama, user_text)
    storage.append("user", user_text, tokens=user_tokens)
    long_memory.append("user", user_text, session_id="", tokens=user_tokens)

    # 2. Append user to window (in-memory, write later)
    window = storage.read_window()
    window.append({"role": "user", "content": user_text})

    # 3. Maybe compact
    compaction_info = {"triggered": False}
    if auto_compact and compaction.needs_compaction(llama, window, t_max=compaction.T_MAX):
        stats = compaction.compact_and_save(
            llama,
            summary_tokens=compaction.SUMMARY_TOKENS,
            t_retained=compaction.T_RETAINED,
        )
        compaction_info = {"triggered": True, "stats": stats}
        window = storage.read_window()

    # 4. Assemble context: system (role + project) + window, with budget
    budget = _load_budget()
    # Separate system summary from window (only one system allowed at start)
    _window_summary = ""
    _window_clean = []
    for _m in window:
        if _m.get("role") == "system":
            _window_summary = _m.get("content", "")
        else:
            _window_clean.append(_m)
    chat_msgs = _to_chat(_window_clean)

    # Routing: auto-select role/project/retrieval filter
    routing = {"role": None, "project": None, "retrieval_filter": None, "auto": False}
    if iris_router is not None:
        try:
            st = _read_state()
            cur_role = (st.get("role") or {}).get("active") or None
            cur_proj = (st.get("project") or {}).get("active") or None
            if not cur_role:
                ro = iris_router.route(user_text, current_role=None, current_project=None)
                routing["role"] = ro.get("role")
                # Only accept project if router actually found one
                found_proj = ro.get("project")
                if found_proj:
                    routing["project"] = found_proj
                routing["retrieval_filter"] = ro.get("retrieval_filter")
                routing["reason"] = ro.get("reason")
                routing["auto"] = True
            else:
                routing["role"] = cur_role
                ro = iris_router.route(user_text, current_role=cur_role)
                routing["retrieval_filter"] = ro.get("retrieval_filter")
                routing["auto"] = False
        except Exception as e:
            routing["error"] = str(e)

    # System = core + role + project (separate caps)
    parts = build_system_message(
        role_override=routing.get("role") if routing.get("auto") else None,
        split=True,
    )
    core_tokens = role_tokens = proj_tokens = 0
    if parts["core"]:
        parts["core"], core_tokens = _truncate_text(llama, parts["core"], budget["core"])
    if parts["role"]:
        parts["role"], role_tokens = _truncate_text(llama, parts["role"], budget["role"])
    if parts["project"]:
        parts["project"], proj_tokens = _truncate_text(llama, parts["project"], budget["project"])
    sys_msg = "\n\n".join(p for p in (parts["core"], parts["role"], parts["project"]) if p)
    sys_tokens = core_tokens + role_tokens + proj_tokens

    # Retrieval from Chroma (independent cap)
    origin_filter = routing.get("retrieval_filter")
    retrieval_text, retrieval_info = _retrieve(
        llama, user_text, top_k=5,
        max_tokens=budget["retrieval"],
        origin_filter=origin_filter,
    )

    # Combine into ONE system message
    combined = sys_msg or ""
    if _window_summary:
        combined = (combined + "\n\n" + _window_summary) if combined else _window_summary
    if retrieval_text:
        combined = (combined + "\n\n" + retrieval_text) if combined else retrieval_text

    if combined:
        chat_msgs = [{"role": "system", "content": combined}] + chat_msgs

    # Truncate last user message if too long
    if chat_msgs:
        last = chat_msgs[-1]
        if last.get("role") == "user":
            trimmed, q_tokens = _truncate_text(llama, last["content"], budget["query"])
            chat_msgs[-1] = {"role": "user", "content": trimmed}

    # 5. Generate (with rollback on failure)
    chat_msgs = _normalize_roles(chat_msgs)
    try:
        r = generate(llama, chat_msgs, max_tokens=max_tokens,
                     temperature=temperature, top_p=top_p)
    except Exception as e:
        # Откат: убираем последний user из window
        window = storage.read_window()
        if window and window[-1].get("role") == "user":
            window.pop()
            storage.write_window(window)
        raise

    # 6. Tool-use: one iteration max
    tool_info = {"called": [], "iterations": 0}
    if iris_tools is not None and iris_parser is not None:
        pr = iris_parser.parse(r["text"])
        if pr["calls"]:
            tool_info["iterations"] = 1
            tool_msgs = list(chat_msgs)
            tool_msgs.append({"role": "assistant", "content": pr["clean_text"] or r["text"]})
            results_block = []
            for c in pr["calls"]:
                name = c["name"]
                args = c["args"]
                res = iris_tools.call(name, **args)
                tool_info["called"].append({
                    "name": name,
                    "args": args,
                    "ok": res.get("ok", False),
                    "error": res.get("error") if not res.get("ok") else None,
                })
                # Format result compactly
                if res.get("ok"):
                    payload = res.get("result", {})
                    if name == "now":
                        txt = payload.get("iso", "?")
                    elif name == "list_dir":
                        items = payload.get("items", [])
                        txt = "count=" + str(payload.get("count", 0)) + "; " + ", ".join([i.get("path", "?") for i in items[:20]])
                    elif name == "read_file":
                        txt = payload.get("text", "")[:2000]
                    elif name == "find_files":
                        matches = payload.get("matches", [])
                        txt = "count=" + str(payload.get("count", 0)) + "; " + ", ".join([m.get("path", "?") for m in matches[:10]])
                    else:
                        txt = str(payload)[:1000]
                else:
                    txt = "ERROR: " + str(res.get("error", "?"))
                results_block.append("[" + name + "] " + txt)
            tool_msg = "\n".join(results_block)
            tool_msgs.append({"role": "user", "content": "[TOOL RESULTS]\n" + tool_msg + "\n\nNow answer the original question, no more tools."})
            # Second call
            r2 = generate(llama, tool_msgs, max_tokens=max_tokens,
                          temperature=temperature, top_p=top_p)
            # Use second answer, strip any remaining tokens
            pr2 = iris_parser.parse(r2["text"])
            r["text"] = pr2["clean_text"] or r2["text"]
            r["completion_tokens"] = r["completion_tokens"] + r2["completion_tokens"]
            r["seconds"] = round(r["seconds"] + r2["seconds"], 2)
            r["tps"] = round(r["completion_tokens"] / r["seconds"], 2) if r["seconds"] > 0 else 0.0
        else:
            r["text"] = pr["clean_text"] or r["text"]

    r["tool_use"] = tool_info

    # Add budget info to result
    r["budget"] = {
        "core_tokens": core_tokens,
        "core_cap": budget["core"],
        "role_tokens": role_tokens,
        "role_cap": budget["role"],
        "project_tokens": proj_tokens,
        "project_cap": budget["project"],
        "retrieval": retrieval_info,
        "retrieval_cap": budget["retrieval"],
        "window_cap": budget["window"],
        "reserve": budget["reserve"],
    }
    r["routing"] = routing

    # 5. Append assistant to both session.log and window
    answer = r["text"]
    storage.append("assistant", answer, tokens=r["completion_tokens"])
    long_memory.append("assistant", answer, session_id="", tokens=r["completion_tokens"])

    # 28b: index dialog pair into Chroma
    try:
        _index_dialog(user_text, answer, session_id="")
    except Exception:
        pass
    window.append({"role": "assistant", "content": answer})
    storage.write_window(window)

    r["compaction"] = compaction_info
    return r


def get_history():
    """Full session.log (all messages, originals)."""
    return storage.read_session()


def get_window():
    """Current working window."""
    return storage.read_window()


def session_stats():
    """Stats about current session + archive."""
    s = storage.stats()
    s["archive"] = long_memory.stats()
    return s


if __name__ == "__main__":
    storage.reset_session()
    r = chat_one("Say: one, two, three.", max_tokens=20)
    print("ANSWER:", r["text"])
    print("TPS:", r["tps"])
    print("STATS:", session_stats())


# ---------- УПРАВЛЕНИЕ МОДЕЛЯМИ ----------

def list_models(weights_dir=None):
    """Список .gguf в папке моделей."""
    if weights_dir is None:
        weights_dir = os.path.join(X, "01_core", "weights")
    if not os.path.isdir(weights_dir):
        return []
    return sorted([f for f in os.listdir(weights_dir) if f.lower().endswith(".gguf")])


def current_model():
    """Имя файла текущей модели или None."""
    global _META
    if _META is not None:
        return _META.get("model")
    # Fallback: читаем active_model.txt до загрузки
    try:
        path = os.path.join(X, "01_core", "active_model.txt")
        with open(path, "r", encoding="utf-8-sig") as f:
            name = f.read().strip()
            return name or None
    except Exception:
        return None


def load_model_by_name(model_name, weights_dir=None):
    """Выгрузить текущую модель, загрузить новую. Возвращает (ok, message)."""
    if weights_dir is None:
        weights_dir = os.path.join(X, "01_core", "weights")
    path = os.path.join(weights_dir, model_name)
    if not os.path.exists(path):
        return False, "Файл не найден: " + path

    # 1. Выгрузить
    reset()

    # 2. Обновить active_model.txt
    try:
        active_file = os.path.join(X, "01_core", "active_model.txt")
        with open(active_file, "w", encoding="utf-8") as f:
            f.write(model_name)
    except Exception as e:
        return False, "Не могу записать active_model.txt: " + str(e)

    # 3. Загрузить
    try:
        llama, meta = get_llama(verbose=False)
        if llama is None:
            return False, "load_model вернул None"
        return True, "Загружено: " + model_name
    except Exception as e:
        return False, "Ошибка загрузки: " + str(e)[:160]
