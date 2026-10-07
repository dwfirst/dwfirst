"""IRIS UI v4 — clean, dark, minimal."""
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
MEM_WORK = os.path.join(X, "03_memory_working")
MEM_LONG = os.path.join(X, "04_memory_long")
CHROMA = os.path.join(X, "05_chroma")
ROUTER = os.path.join(X, "07_router")
TOOLS = os.path.join(X, "08_tools")
ORCH = os.path.join(X, "07_router", "orchestrator.py")
LOGS = os.path.join(X, "93_logs")

for d in (MODULES, PROJECTS, REFLECT, INBOX, MEM_WORK, MEM_LONG, CHROMA, ROUTER, TOOLS):
    if d not in sys.path:
        sys.path.insert(0, d)

os.makedirs(LOGS, exist_ok=True)
UI_LOG = os.path.join(LOGS, "ui.log")


def log(msg):
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


import brain


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


orch = get_orch()
working = get_working()
night = get_night()
ingest_mod = get_ingest()

st.set_page_config(page_title="IRIS", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
:root {
  --bg: #0a0c10;
  --panel: #0f1218;
  --card: #141821;
  --border: #1f2530;
  --text: #e6edf3;
  --muted: #6e7681;
  --accent: #58a6ff;
  --ok: #3fb950;
  --radius: 8px;
}
html, body, .stApp {
  background: var(--bg) !important;
  color: var(--text);
  font-family: 'Segoe UI', system-ui, sans-serif;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 4.2rem 1.4rem 0.8rem 1.4rem !important; max-width: 100% !important; }

/* Sidebar */
[data-testid="stSidebar"] {
  background: var(--panel) !important;
  border-right: 1px solid var(--border);
  min-width: 260px !important;
  max-width: 260px !important;
}
[data-testid="stSidebar"] > div:first-child { padding: 1rem 1rem !important; }
[data-testid="stSidebar"] h3 {
  font-family: monospace; font-size: 0.68rem; text-transform: uppercase;
  letter-spacing: 0.15em; color: var(--muted);
  margin: 1rem 0 0.5rem 0; font-weight: 500;
}
[data-testid="stSidebar"] h3:first-child { margin-top: 0; }

/* Top bar */
.topbar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 16px; margin-bottom: 16px;
  border-bottom: 1px solid var(--border);
  font-family: monospace; font-size: 0.75rem; color: var(--muted);
}
.topbar .logo { color: var(--accent); letter-spacing: 0.2em; font-weight: 600; }
.topbar .stat { margin-left: 18px; }
.topbar .stat b { color: var(--text); font-weight: 500; }
.topbar .dot { color: var(--ok); margin-right: 4px; }

/* Chat */
.stChatMessage {
  background: transparent !important; border: none !important;
  padding: 0.6rem 0 !important;
}
.stChatMessage [data-testid="stChatMessageAvatarUser"] { display: none; }
.stChatMessage [data-testid="stChatMessageAvatarAssistant"] { display: none; }
.stChatMessage [data-testid="stChatMessageContent"] {
  background: var(--card); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 14px 18px;
}
.stChatInput textarea {
  background: var(--card) !important; color: var(--text) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  font-size: 0.9rem !important;
}
.stChatInput textarea:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 1px var(--accent) !important;
}

/* Buttons */
.stButton > button {
  background: var(--card); color: var(--text);
  border: 1px solid var(--border); border-radius: var(--radius);
  font-size: 0.75rem; width: auto; min-width: 140px;
  padding: 4px 14px; height: 28px; line-height: 1;
}
[data-testid="stSidebar"] .stButton > button { width: 100%; }
.stButton > button:hover { border-color: var(--accent); color: var(--accent); }
.stButton > button:disabled { opacity: 0.3; }

/* Select */
.stSelectbox div[data-baseweb="select"] > div {
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  font-size: 0.8rem; color: var(--text) !important;
}

/* Status */
.statusbar {
  font-family: monospace; font-size: 0.7rem; color: var(--muted);
  border-top: 1px solid var(--border);
  padding: 8px 0; margin-top: 12px;
}
.statusbar b { color: var(--text); }
.statusbar .sep { margin: 0 10px; color: var(--border); }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
/* Fix sidebar — always visible */
[data-testid="stSidebar"] {
  background: var(--panel) !important;
  border-right: 1px solid var(--border) !important;
  min-width: 280px !important;
  max-width: 280px !important;
  transform: none !important;
  visibility: visible !important;
}
[data-testid="stSidebarCollapseButton"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
[data-testid="stSidebarNav"] { display: none; }
[data-testid="stSidebar"] {
  min-width: 280px !important;
  max-width: 280px !important;
  transform: none !important;
  visibility: visible !important;
}
[data-testid="stSidebar"] .stButton > button {
  width: 100% !important;
  height: 32px !important;
  padding: 4px 12px !important;
  font-size: 0.78rem !important;
  margin-bottom: 6px !important;
  line-height: 1 !important;
  text-align: left !important;
}
[data-testid="stSidebar"] [data-testid="column"] {
  width: 100% !important;
  flex: 1 1 100% !important;
  min-width: 100% !important;
}

/* Top bar — видимая карточка */
.topbar {
  display: flex !important; align-items: center; justify-content: space-between;
  padding: 12px 18px !important; margin: 0 0 18px 0 !important;
  position: fixed !important; top: 0 !important; left: 280px !important;
  right: 0 !important; z-index: 999 !important; backdrop-filter: blur(8px);
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  font-family: monospace; font-size: 0.78rem; color: var(--muted);
  min-height: 44px;
}
.topbar .logo { color: var(--accent); letter-spacing: 0.22em; font-weight: 600; font-size: 0.85rem; }
.topbar .stat { margin-left: 20px; }
.topbar .stat b { color: var(--text); font-weight: 500; }
.topbar .dot { color: var(--ok); margin-right: 5px; font-size: 0.9rem; }

/* Chat — различаем user / assistant */
.stChatMessage { background: transparent !important; border: none !important; padding: 0.5rem 0 !important; }
.stChatMessage [data-testid="stChatMessageContent"] {
  border-radius: var(--radius); padding: 14px 18px;
}
.stChatMessage [data-testid="stChatMessageContent"] p { margin: 0; line-height: 1.55; }
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"],
.stChatMessage:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"] {
  background: var(--card);
  border: 1px solid var(--border);
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) [data-testid="stChatMessageContent"],
.stChatMessage:has([data-testid="chatAvatarIcon-assistant"]) [data-testid="stChatMessageContent"] {
  background: transparent;
  border: 1px solid transparent;
  border-left: 2px solid var(--accent);
}
</style>
""", unsafe_allow_html=True)


# ---- SIDEBAR ----
with st.sidebar:
    st.markdown("### Модель")
    models = brain.list_models()
    if models:
        current = brain.current_model()
        idx = models.index(current) if current in models else 0
        choice = st.selectbox("m", models, index=idx, key="m", label_visibility="collapsed")
        if st.button("Загрузить", key="b_load"):
            with st.spinner("..."):
                ok, msg = brain.load_model_by_name(choice)
            st.caption(msg if ok else f"ERR: {msg[:60]}")
    else:
        st.caption("нет .gguf")



    st.markdown("### Память")
    try:
        ws = working.stats()
        st.caption(f"фактов: {ws.get('total', 0)}")
    except Exception:
        st.caption("—")
    if st.button("Индексировать inbox", key="b_ing"):
        with st.spinner("..."):
            _, err = safe(ingest_mod.run)
        st.caption("готово" if not err else f"ERR: {err[:60]}")

    st.markdown("### Журналы")
    for origin, label in (("inner_voice", "голос"), ("reverie", "грёзы")):
        try:
            facts = working.get_by_origin(origin, days=7)
            with st.expander(f"{label} · {len(facts)}"):
                if not facts:
                    st.caption("пусто")
                else:
                    for f in facts[-3:]:
                        d = f.get("date", "")[:16]
                        t = (f.get("text", "") or "")[:400]
                        st.markdown(f"**{d}**  \n{t}")
        except Exception as e:
            st.caption(f"{label}: ошибка")
    st.markdown("### Рефлексия")
    conf = st.checkbox("подтверждаю", key="c_night")
    if st.button("Сон", key="b_sleep", disabled=not conf):
        with st.spinner("Сон..."):
            try:
                llama, _ = brain.get_llama()
                r, err = safe(night.run, llama, mode="sleep")
            except Exception as e:
                err, r = str(e), None
        if err:
            st.caption(f"ERR: {err[:60]}")
        elif r:
            st.caption(f"{r.get('stages_ok',0)}/{r.get('stages_run',0)} за {r.get('elapsed',0)}с")
    if st.button("Грёзы", key="b_reverie", disabled=not conf):
        with st.spinner("Грёзы..."):
            try:
                llama, _ = brain.get_llama()
                r, err = safe(night.run, llama, mode="reverie")
            except Exception as e:
                err, r = str(e), None
        if err:
            st.caption(f"ERR: {err[:60]}")
        elif r:
            st.caption(f"{r.get('stages_ok',0)}/{r.get('stages_run',0)} за {r.get('elapsed',0)}с")


# ---- TOP BAR ----
try:
    stt = orch.run("state")["result"]
    pass
except Exception:
    pass
model_now = brain.current_model() or "—"

st.markdown(f"""
<div class="topbar">
  <div>
    <span class="logo">IRIS</span>
    <span class="stat"><span class="dot">●</span>model <b>{model_now[:24]}</b></span>

  </div>
</div>
""", unsafe_allow_html=True)


# ---- CHAT ----
def stream_response(prompt):
    r = brain.chat_one(prompt, max_tokens=512)
    text = r.get("text", "")
    chunk = 3
    for i in range(0, len(text), chunk):
        yield text[i:i + chunk]


try:
    history = brain.get_window()
except Exception:
    history = []

for m in history[-20:]:
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
            st.caption(f"ошибка: {str(e)[:80]}")


# ---- STATUS ----
try:
    ss = brain.session_stats()
    sm = ss.get("session_messages", 0)
    at = ss.get("archive", {}).get("total", 0)
except Exception:
    sm, at = 0, 0

st.markdown(f"""
<div class="statusbar">
  сессия <b>{sm}</b><span class="sep">·</span>архив <b>{at}</b><span class="sep">·</span>модель <b>{model_now[:24]}</b>
</div>
""", unsafe_allow_html=True)