"""IRIS UI v3 — minimalist cockpit."""
import os
import sys
import importlib.util
import datetime

import streamlit as st

X = "X:" + os.sep
MODULES = os.path.join(X, "01_core", "modules")
PROJECTS = os.path.join(X, "10_projects")
REFLECT = os.path.join(X, "06_reflection")
INBOX = os.path.join(X, "09_inbox")
ORCH = os.path.join(X, "07_router", "orchestrator.py")
LOGS = os.path.join(X, "93_logs")
MEM_WORK = os.path.join(X, "03_memory_working")
MEM_LONG = os.path.join(X, "04_memory_long")
CHROMA = os.path.join(X, "05_chroma")
ROUTER = os.path.join(X, "07_router")
TOOLS = os.path.join(X, "08_tools")
for d in (MODULES, PROJECTS, REFLECT, INBOX, MEM_WORK, MEM_LONG, CHROMA, ROUTER, TOOLS):
    if d not in sys.path:
        sys.path.insert(0, d)

os.makedirs(LOGS, exist_ok=True)
UI_LOG = os.path.join(LOGS, "ui.log")


def log(msg: str) -> None:
    try:
        with open(UI_LOG, "a", encoding="utf-8") as f:
            f.write(f"{datetime.datetime.now().isoformat()}\t{msg}\n")
    except Exception:
        pass


def safe(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs), None
    except Exception as e:
        msg = f"{type(e).__name__}: {e}"
        log(msg)
        return None, msg


import brain  # noqa: E402


@st.cache_resource
def get_orch():
    spec = importlib.util.spec_from_file_location("iris_orch", ORCH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@st.cache_resource
def get_working():
    import working
    return working


@st.cache_resource
def get_night():
    import night_mode
    return night_mode


@st.cache_resource
def get_ingest():
    import ingest
    return ingest


@st.cache_resource
def get_indexer():
    import indexer
    return indexer


orch = get_orch()
working = get_working()
night = get_night()
ingest_mod = get_ingest()
indexer = get_indexer()

st.set_page_config(page_title="IRIS", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
:root {
  --bg: #0a0c10;
  --panel: #12151c;
  --card: #161a23;
  --card-hover: #1c212c;
  --border: #232936;
  --text: #e6edf3;
  --muted: #7d8590;
  --accent: #58a6ff;
  --accent-dim: rgba(88,166,255,0.12);
  --ok: #3fb950;
  --warn: #d29922;
  --danger: #f85149;
  --radius: 10px;
  --radius-sm: 6px;
}
html, body, .stApp {
  background: var(--bg) !important;
  color: var(--text);
  font-family: 'Segoe UI', -apple-system, system-ui, sans-serif;
}
.block-container { padding: 0.5rem 1.2rem 0.4rem 1.2rem !important; max-width: 100% !important; }
#MainMenu, footer, header { visibility: hidden; }

/* --- Top bar --- */
.topbar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 16px; border-bottom: 1px solid var(--border);
  font-size: 0.78rem; color: var(--muted); font-family: 'JetBrains Mono', monospace;
  background: var(--panel); border-radius: var(--radius);
  margin-bottom: 12px;
}
.topbar .logo { color: var(--accent); letter-spacing: 0.2em; font-weight: 600; font-size: 0.85rem; }
.topbar .stat { margin-left: 20px; }
.topbar .stat b { color: var(--text); font-weight: 500; }
.topbar .dot { display: inline-block; width: 6px; height: 6px; border-radius: 50%;
  background: var(--ok); margin-right: 6px; vertical-align: middle; }

/* --- Sidebar --- */
[data-testid="stSidebar"] {
  background: var(--panel) !important;
  border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] .block-container { padding: 0.8rem 0.8rem !important; }

.side-card {
  background: var(--card); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 14px 14px 10px 14px;
  margin-bottom: 12px;
}
.side-card-title {
  font-family: 'JetBrains Mono', monospace; font-size: 0.68rem;
  text-transform: uppercase; letter-spacing: 0.15em; color: var(--muted);
  margin-bottom: 10px; padding-bottom: 8px; border-bottom: 1px solid var(--border);
}

/* --- Chat messages --- */
.stChatMessage {
  background: transparent !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  padding: 12px 16px !important;
  margin-bottom: 8px !important;
}
.stChatMessage:hover { border-color: #2d3546 !important; }
[data-testid="chatAvatarIcon-user"] { background: var(--accent) !important; }
[data-testid="chatAvatarIcon-assistant"] { background: var(--muted) !important; }

/* --- Input --- */
.stChatInput textarea {
  background: var(--card) !important; color: var(--text) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  font-size: 0.9rem !important; padding: 12px 14px !important;
}
.stChatInput textarea:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 2px var(--accent-dim) !important;
}

/* --- Buttons --- */
.stButton > button {
  background: var(--card); color: var(--text);
  border: 1px solid var(--border); border-radius: var(--radius-sm);
  font-size: 0.78rem; padding: 6px 12px;
  transition: all 0.12s ease;
}
.stButton > button:hover {
  border-color: var(--accent); color: var(--accent);
  background: var(--card-hover);
}
.stButton > button:disabled { opacity: 0.3; }

/* --- Selectbox --- */
.stSelectbox div[data-baseweb="select"] > div {
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-sm) !important;
  font-size: 0.82rem;
  color: var(--text) !important;
}

/* --- Checkbox --- */
.stCheckbox { font-size: 0.8rem; }

/* --- Status bar --- */
.statusbar {
  font-size: 0.7rem; color: var(--muted); font-family: 'JetBrains Mono', monospace;
  border-top: 1px solid var(--border); padding: 8px 0; margin-top: 8px;
}
.statusbar b { color: var(--text); }
.statusbar .sep { margin: 0 8px; color: var(--border); }

/* --- Scrollbar --- */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--muted); }
</style>
""", unsafe_allow_html=True)


@st.fragment
def sidebar_model():
    st.markdown("### Модель")
    models = brain.list_models()
    if not models:
        st.caption("Нет .gguf в 01_core/weights")
        return
    current = brain.current_model()
    idx = models.index(current) if current in models else 0
    choice = st.selectbox("model", models, index=idx, key="model_pick",
                          label_visibility="collapsed")
    if st.button("Загрузить", use_container_width=True, key="btn_load_model"):
        with st.spinner(f"Переключаю на {choice}..."):
            ok, msg = brain.load_model_by_name(choice)
        if ok:
            st.success(msg)
            log(f"model loaded: {choice}")
        else:
            st.caption(f"Ошибка: {msg}")


@st.fragment
def sidebar_context():
    st.markdown("### Контекст")
    try:
        state = orch.run("state")["result"]
        role_now = state["role"]["active"] or "—"
        proj_now = state["project"]["active"] or "—"
    except Exception:
        role_now, proj_now = "—", "—"

    roles_dir = os.path.join(X, "11_roles")
    roles = sorted([d for d in os.listdir(roles_dir)
                    if os.path.isdir(os.path.join(roles_dir, d))])
    ridx = roles.index(role_now) + 1 if role_now in roles else 0
    new_role = st.selectbox("Роль", ["—"] + roles, index=ridx, key="sel_role")
    if st.button("Применить роль", use_container_width=True, key="btn_role"):
        if new_role != "—":
            orch.run("set_role", role=new_role)
            st.rerun()

    items = []
    proot = os.path.join(X, "10_projects")
    if os.path.isdir(proot):
        for cat in sorted(os.listdir(proot)):
            cpath = os.path.join(proot, cat)
            if os.path.isdir(cpath) and not cat.startswith("_"):
                for proj in sorted(os.listdir(cpath)):
                    if os.path.isdir(os.path.join(cpath, proj)):
                        items.append(cat + "/" + proj)
    pidx = items.index(proj_now) + 1 if proj_now in items else 0
    new_proj = st.selectbox("Проект", ["—"] + items, index=pidx, key="sel_proj")
    if st.button("Применить проект", use_container_width=True, key="btn_proj"):
        if new_proj != "—":
            orch.run("set_project", project=new_proj)
            st.rerun()


@st.fragment
def sidebar_memory():
    st.markdown("### Память")
    try:
        wstats = working.stats()
        st.caption(f"active {wstats.get('active', 0)} / total {wstats.get('total', 0)}")
    except Exception:
        st.caption("—")
    if st.button("Индексировать 09_inbox", use_container_width=True, key="btn_ingest"):
        with st.spinner("Ingest..."):
            _, err = safe(ingest_mod.run)
        if err:
            st.caption(f"Ошибка: {err[:80]}")
        else:
            st.success("Готово")
    if st.button("Обновить метаданные", use_container_width=True, key="btn_meta"):
        with st.spinner("Indexer..."):
            metas, err = safe(indexer.update_all)
        if err:
            st.caption(f"Ошибка: {err[:80]}")
        else:
            st.success(f"Обновлено: {len(metas)}")


@st.fragment
def sidebar_reflection():
    st.markdown("### Рефлексия")
    st.caption("Ночной режим: Дневник -> Голос -> Сны")
    confirm = st.checkbox("Подтверждаю", key="confirm_night")
    if st.button("Запустить ночной режим", use_container_width=True,
                 key="btn_night", disabled=not confirm):
        with st.spinner("Ночной режим... Это долго."):
            try:
                llama, _ = brain.get_llama()
                r, err = safe(night.run, llama)
            except Exception as e:
                err = str(e); r = None
        if err:
            st.caption(f"Ошибка: {err[:80]}")
        elif r:
            ok_n = r.get("stages_ok", 0)
            tot = r.get("stages_run", 0)
            el = r.get("elapsed", 0)
            st.success(f"{ok_n}/{tot} стадий за {el} сек")


with st.sidebar:
    sidebar_model()
    sidebar_context()
    sidebar_memory()
    sidebar_reflection()


try:
    state = orch.run("state")["result"]
    role_now = state["role"]["active"] or "—"
    proj_now = state["project"]["active"] or "—"
except Exception:
    role_now, proj_now = "—", "—"

model_now = brain.current_model() or "—"

st.markdown(f"""
<div class="topbar">
  <div>
    <span class="logo">IRIS</span>
    <span class="stat">model <b>{model_now}</b></span>
    <span class="stat">role <b>{role_now}</b></span>
    <span class="stat">project <b>{proj_now}</b></span>
  </div>
</div>
""", unsafe_allow_html=True)


def stream_response(prompt: str):
    r = brain.chat_one(prompt, max_tokens=512)
    text = r.get("text", "")
    chunk = 3
    for i in range(0, len(text), chunk):
        yield text[i:i + chunk]


try:
    history = brain.get_window()
except Exception:
    history = []

for m in history[-16:]:
    with st.chat_message(m["role"]):
        st.write(m["content"])

if prompt := st.chat_input("Сообщение..."):
    with st.chat_message("user"):
        st.write(prompt)
    with st.chat_message("assistant"):
        try:
            st.write_stream(stream_response(prompt))
        except Exception as e:
            log(f"chat error: {e}")
            st.caption(f"Модуль недоступен: {str(e)[:80]}")


try:
    sstats = brain.session_stats()
    sess_msgs = sstats.get("session_messages", 0)
    arch_total = sstats.get("archive", {}).get("total", 0)
except Exception:
    sess_msgs, arch_total = 0, 0

st.markdown(f"""
<div class="statusbar">
  memory <b>OK</b> &nbsp;·&nbsp;
  session msgs <b>{sess_msgs}</b> &nbsp;·&nbsp;
  archive <b>{arch_total}</b> &nbsp;·&nbsp;
  model <b>{model_now}</b>
</div>
""", unsafe_allow_html=True)