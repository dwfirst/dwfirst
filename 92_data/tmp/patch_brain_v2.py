# patch_brain_v2.py - tochechno menyaem 4 mestа v brain.py
import io, os

X = "X:" + os.sep
p = os.path.join(X, "01_core", "modules", "brain.py")

with io.open(p, "r", encoding="utf-8-sig") as f:
    src = f.read()

# --- 1) _load_budget ---
old_budget = '''def _load_budget():
    """Read budget section from config.json."""
    cfg_path = os.path.join(X, "00_dna", "config.json")
    defaults = {"role": 400, "retrieval": 1200, "window": 3000, "query": 500, "reserve": 600}
    if not os.path.exists(cfg_path):
        return defaults
    try:
        import json as _json
        with open(cfg_path, "r", encoding="utf-8-sig") as f:
            cfg = _json.load(f)
        b = cfg.get("budget", {})
        # backward compat: old "system" -> new "role"
        role_cap = b.get("role", b.get("system", 400))
        return {
            "role": role_cap,
            "retrieval": b.get("retrieval", 1200),
            "window": b.get("window", 3000),
            "query": b.get("query", 500),
            "reserve": b.get("reserve", 600),
        }
    except Exception:
        return defaults'''

new_budget = '''def _load_budget():
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
        return defaults'''

if old_budget not in src:
    raise SystemExit("BLOCK1 not found")
src = src.replace(old_budget, new_budget, 1)


# --- 2) build_system_message ---
old_bsm = '''def build_system_message(role_override=None):
    """Build system message from active role + project. Returns str or ''."""
    state = _read_state()
    parts = []

    # --- role ---
    role = role_override or (state.get("role") or {}).get("active") or ""
    if role:
        rdir = os.path.join(ROLES_DIR, role)
        if os.path.isdir(rdir):
            block = ["[ROLE: " + role + "]"]
            for fname in ("prompt.md", "style.md", "rules.md"):
                raw = _read_file_safe(os.path.join(rdir, fname))
                content = _clean_role_file(raw)
                if content:
                    block.append(content)
            if len(block) > 1:
                parts.append("\\n".join(block))

    # --- project ---
    proj = (state.get("project") or {}).get("active") or ""
    if proj and "/" in proj:
        cat, name = proj.split("/", 1)
        pdir = os.path.join(PROJECTS_DIR, cat, name)
        if os.path.isdir(pdir):
            block = ["[PROJECT: " + proj + "]"]
            raw = _read_file_safe(os.path.join(pdir, "context.md"))
            ctx = _clean_role_file(raw, min_chars=80)
            if ctx:
                block.append(ctx)
            else:
                # context.md is a stub - use project card from meta.json
                card = _project_card(cat, name)
                if card:
                    block.append(card)
            if len(block) > 1:
                parts.append("\\n".join(block))

    if not parts:
        return ""
    return "\\n\\n".join(parts)'''

new_bsm = '''def build_system_message(role_override=None, split=False):
    """Build system message from core identity + active role + project.
    split=True: returns {"core": str, "role": str, "project": str}.
    split=False: returns joined string (backward compat)."""
    state = _read_state()
    out = {"core": "", "role": "", "project": ""}

    # --- core identity ---
    core_path = os.path.join(X, "00_dna", "identity_core.md")
    core_raw = _read_file_safe(core_path)
    if core_raw:
        cleaned = _clean_role_file(core_raw, min_chars=50)
        out["core"] = cleaned or core_raw

    # --- role (prompt.md, style.md, rules.md) ---
    role = role_override or (state.get("role") or {}).get("active") or ""
    if role:
        rdir = os.path.join(ROLES_DIR, role)
        if os.path.isdir(rdir):
            block = ["[ROLE: " + role + "]"]
            for fname in ("prompt.md", "style.md", "rules.md"):
                raw = _read_file_safe(os.path.join(rdir, fname))
                content = _clean_role_file(raw)
                if content:
                    block.append(content)
            if len(block) > 1:
                out["role"] = "\\n".join(block)

    # --- project ---
    proj = (state.get("project") or {}).get("active") or ""
    if proj and "/" in proj:
        cat, name = proj.split("/", 1)
        pdir = os.path.join(PROJECTS_DIR, cat, name)
        if os.path.isdir(pdir):
            block = ["[PROJECT: " + proj + "]"]
            raw = _read_file_safe(os.path.join(pdir, "context.md"))
            ctx = _clean_role_file(raw, min_chars=80)
            if ctx:
                block.append(ctx)
            else:
                card = _project_card(cat, name)
                if card:
                    block.append(card)
            if len(block) > 1:
                out["project"] = "\\n".join(block)

    if split:
        return out
    parts = [out["core"], out["role"], out["project"]]
    parts = [p for p in parts if p]
    return "\\n\\n".join(parts)'''

if old_bsm not in src:
    raise SystemExit("BLOCK2 not found")
src = src.replace(old_bsm, new_bsm, 1)


# --- 3) chat_one: system + retrieval ---
old_c1 = '''    # System = role + project (independent cap)
    sys_msg = build_system_message(role_override=routing.get("role") if routing.get("auto") else None)
    sys_tokens = 0
    if sys_msg:
        sys_msg, sys_tokens = _truncate_text(llama, sys_msg, budget["role"])

    # Retrieval from Chroma (independent cap)
    origin_filter = routing.get("retrieval_filter")
    retrieval_text, retrieval_info = _retrieve(llama, user_text, top_k=5, max_tokens=budget["retrieval"], origin_filter=origin_filter)

    # Combine: role block + retrieval block
    combined = sys_msg or ""
    if retrieval_text:
        if combined:
            combined = combined + "\\n\\n" + retrieval_text
        else:
            combined = retrieval_text

    if combined:
        chat_msgs = [{"role": "system", "content": combined}] + chat_msgs'''

new_c1 = '''    # System = core + role + project (separate caps)
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
    sys_msg = "\\n\\n".join(p for p in (parts["core"], parts["role"], parts["project"]) if p)
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
    if retrieval_text:
        combined = (combined + "\\n\\n" + retrieval_text) if combined else retrieval_text

    if combined:
        chat_msgs = [{"role": "system", "content": combined}] + chat_msgs'''

if old_c1 not in src:
    raise SystemExit("BLOCK3 not found")
src = src.replace(old_c1, new_c1, 1)


# --- 4) r["budget"] ---
old_c2 = '''    r["budget"] = {
        "role_tokens": sys_tokens,
        "role_cap": budget["role"],
        "retrieval": retrieval_info,
        "window_cap": budget["window"],
        "reserve": budget["reserve"],
    }'''

new_c2 = '''    r["budget"] = {
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
    }'''

if old_c2 not in src:
    raise SystemExit("BLOCK4 not found")
src = src.replace(old_c2, new_c2, 1)

with io.open(p, "w", encoding="utf-8") as f:
    f.write(src)
print("patched_brain_v2 OK")