"""IRIS UI - cockpit with all controls wired."""
import os
import sys
import importlib.util
import json

import streamlit as st

X = "X:" + os.sep
ORCH = os.path.join(X, "07_router", "orchestrator.py")
MODULES = os.path.join(X, "01_core", "modules")
PROJECTS = os.path.join(X, "10_projects")
REFLECT = os.path.join(X, "06_reflection")
INBOX = os.path.join(X, "09_inbox")
for d in (MODULES, PROJECTS, REFLECT, INBOX):
    if d not in sys.path:
        sys.path.insert(0, d)


@st.cache_resource
def get_orch():
    spec = importlib.util.spec_from_file_location("iris_orch", ORCH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@st.cache_resource
def get_brain():
    import brain
    return brain


@st.cache_resource
def get_working():
    sys.path.insert(0, os.path.join(X, "03_memory_working"))
    import working
    return working


@st.cache_resource
def get_night():
    import night_mode
    return night_mode


@st.cache_resource
def get_reflect():
    import diary, inner_voice, dream
    return {"diary": diary, "inner_voice": inner_voice, "dream": dream}


@st.cache_resource
def get_ingest():
    import ingest
    return ingest


@st.cache_resource
def get_indexer():
    import indexer
    return indexer


orch = get_orch()
brain = get_brain()
working = get_working()
night = get_night()
reflect = get_reflect()
ingest_mod = get_ingest()
indexer = get_indexer()

st.set_page_config(page_title="IRIS", layout="wide", initial_sidebar_state="collapsed")

# ---------------- CSS ----------------
st.markdown("""
<style>
:root {
  --bg: #0d1117;
  --panel: #161b22;
  --panel-2: #1c2128;
  --border: #30363d;
  --text: #c9d1d9;
  --muted: #8b949e;
  --accent: #58a6ff;
  --warm: #d29922;
  --ok: #3fb950;
  --danger: #f85149;
  --mono: 'JetBrains Mono', 'Consolas', 'Menlo', monospace;
}
html, body, .stApp { background: var(--bg) !important; color: var(--text); }
.block-container { padding: 0.8rem 1.4rem 1rem 1.4rem !important; max-width: 100% !important; }
#MainMenu, footer, header {visibility: hidden;}
h1, h2, h3, h4 { color: var(--text); font-weight: 500; letter-spacing: 0.02em; font-family: var(--mono); }
h3 { font-size: 0.85rem; text-transform: uppercase; color: var(--muted); margin: 0.4rem 0 0.6rem 0; }

.iris-bar { display: flex; align-items: center; justify-content: space-between;
  background: var(--panel); border: 1px solid var(--border); border-radius: 6px;
  padding: 10px 16px; font-family: var(--mono); font-size: 0.82rem; margin-bottom: 10px; }
.iris-bar .logo { color: var(--accent); font-weight: 600; letter-spacing: 0.15em; }
.iris-bar .stat { color: var(--muted); margin-left: 18px; }
.iris-bar .stat b { color: var(--text); font-weight: 500; }

.mod { background: var(--panel); border: 1px solid var(--border); border-radius: 6px;
  padding: 12px 14px; margin-bottom: 10px; }
.mod-title { font-family: var(--mono); font-size: 0.72rem; text-transform: uppercase;
  letter-spacing: 0.18em; color: var(--muted); margin-bottom: 8px; padding-bottom: 6px;
  border-bottom: 1px solid var(--border); }

.stChatMessage { background: var(--panel) !important; border: 1px solid var(--border) !important; border-radius: 6px !important; }
.stChatMessage [data-testid="chatAvatarIcon-user"] { background: var(--accent) !important; }
.stChatMessage [data-testid="chatAvatarIcon-assistant"] { background: var(--warm) !important; }

.stTextArea textarea, .stTextInput input, .stChatInput textarea {
  background: var(--panel-2) !important; color: var(--text) !important;
  border: 1px solid var(--border) !important; border-radius: 6px !important;
  font-family: var(--mono) !important; }
.stTextArea textarea:focus, .stChatInput textarea:focus { border-color: var(--accent) !important; box-shadow: 0 0 0 1px var(--accent) !important; }

.stButton > button { background: var(--panel-2); color: var(--text);
  border: 1px solid var(--border); border-radius: 6px; font-family: var(--mono);
  font-size: 0.78rem; letter-spacing: 0.03em; transition: all 0.12s ease; }
.stButton > button:hover { border-color: var(--accent); color: var(--accent); background: var(--panel); }
.stButton > button:active { transform: translateY(1px); }

.stSelectbox div[data-baseweb="select"] > div { background: var(--panel-2) !important;
  border: 1px solid var(--border) !important; border-radius: 6px !important;
  font-family: var(--mono); font-size: 0.8rem; }

.stTabs [data-baseweb="tab-list"] { gap: 4px; border-bottom: 1px solid var(--border); }
.stTabs [data-baseweb="tab"] { background: transparent; color: var(--muted);
  border-radius: 4px 4px 0 0; font-family: var(--mono); font-size: 0.78rem;
  text-transform: uppercase; letter-spacing: 0.1em; padding: 6px 12px; }
.stTabs [aria-selected="true"] { background: var(--panel); color: var(--accent) !important; border-bottom: 2px solid var(--accent); }

[data-testid="stMetricValue"] { color: var(--text); font-family: var(--mono); font-size: 1.3rem; }
[data-testid="stMetricLabel"] { color: var(--muted); font-family: var(--mono); font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.15em; }
hr { border-color: var(--border); }

.pill { display: inline-block; border: 1px solid var(--border); border-radius: 999px;
  padding: 2px 10px; font-family: var(--mono); font-size: 0.7rem; color: var(--muted);
  margin-right: 6px; margin-bottom: 4px; }
.pill.hot { border-color: var(--accent); color: var(--accent); }
.pill.warm { border-color: var(--warm); color: var(--warm); }

.warn-box {
  background: rgba(210, 153, 34, 0.08);
  border: 1px solid rgba(210, 153, 34, 0.4);
  border-radius: 6px; padding: 10px 12px;
  font-family: var(--mono); font-size: 0.78rem; color: var(--warm);
  margin: 8px 0;
}
.info-box {
  background: rgba(88, 166, 255, 0.06);
  border: 1px solid rgba(88, 166, 255, 0.35);
  border-radius: 6px; padding: 10px 12px;
  font-family: var(--mono); font-size: 0.78rem; color: var(--accent);
  margin: 8px 0;
}
.ok-box {
  background: rgba(63, 185, 80, 0.08);
  border: 1px solid rgba(63, 185, 80, 0.4);
  border-radius: 6px; padding: 10px 12px;
  font-family: var(--mono); font-size: 0.78rem; color: var(--ok);
  margin: 8px 0;
}

::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }
</style>
""", unsafe_allow_html=True)

# ---------------- Top bar ----------------
try:
    state = orch.run("state")["result"]
    role_now = state["role"]["active"] or "—"
    proj_now = state["project"]["active"] or "—"
    sess_now = state["session"]["id"] or "—"
except Exception:
    role_now, proj_now, sess_now = "—", "—", "—"

try:
    sstats = brain.session_stats()
    sess_msgs = sstats["session_messages"]
    arch_total = sstats.get("archive", {}).get("total", 0)
except Exception:
    sess_msgs, arch_total = 0, 0

st.markdown(f"""
<div class="iris-bar">
  <div>
    <span class="logo">IRIS</span>
    <span class="stat">role <b>{role_now}</b></span>
    <span class="stat">project <b>{proj_now}</b></span>
    <span class="stat">session <b>{sess_now}</b></span>
  </div>
  <div>
    <span class="stat">msgs <b>{sess_msgs}</b></span>
    <span class="stat">archive <b>{arch_total}</b></span>
  </div>
</div>
""", unsafe_allow_html=True)

# ---------------- 3-zone layout ----------------
col_l, col_c, col_r = st.columns([1, 1.618, 1])

# ============ LEFT: controls ============
with col_l:
    # ---- ROLE ----
    st.markdown('<div class="mod"><div class="mod-title">Role</div>', unsafe_allow_html=True)
    roles_dir = os.path.join(X, "11_roles")
    roles = sorted([d for d in os.listdir(roles_dir) if os.path.isdir(os.path.join(roles_dir, d))])
    idx_r = roles.index(role_now) + 1 if role_now in roles else 0
    new_role = st.selectbox("ROLE", ["—"] + roles, index=idx_r, key="sel_role")
    if st.button("SET ROLE", use_container_width=True, key="btn_role"):
        if new_role != "—":
            orch.run("set_role", role=new_role)
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # ---- PROJECT ----
    st.markdown('<div class="mod"><div class="mod-title">Project</div>', unsafe_allow_html=True)
    items = []
    proot = os.path.join(X, "10_projects")
    for cat in sorted(os.listdir(proot)):
        cpath = os.path.join(proot, cat)
        if os.path.isdir(cpath) and not cat.startswith("_"):
            for proj in sorted(os.listdir(cpath)):
                if os.path.isdir(os.path.join(cpath, proj)):
                    items.append(cat + "/" + proj)
    idx_p = items.index(proj_now) + 1 if proj_now in items else 0
    new_proj = st.selectbox("PROJECT", ["—"] + items, index=idx_p, key="sel_proj")
    if st.button("SET PROJECT", use_container_width=True, key="btn_proj"):
        if new_proj != "—":
            orch.run("set_project", project=new_proj)
            st.rerun()
    if st.button("UPDATE META", use_container_width=True, key="btn_meta"):
        try:
            metas = indexer.update_all()
            st.success(f"updated {len(metas)} projects")
        except Exception as e:
            st.error(str(e))
    st.markdown('</div>', unsafe_allow_html=True)

    # ---- NIGHT MODE ----
    st.markdown('<div class="mod"><div class="mod-title">Night Mode</div>', unsafe_allow_html=True)
    st.markdown('<div class="warn-box">Запускает Дневник → Голос → Сны. Займёт 5–10 минут. Не закрывай вкладку и не выключай ПК.</div>', unsafe_allow_html=True)
    confirm_night = st.checkbox("Я готов, запускать", key="confirm_night")
    if st.button("RUN NIGHT", use_container_width=True, key="btn_night", disabled=not confirm_night):
        with st.spinner("Ночной режим... Это долго. Смотри сюда, не уходи."):
            try:
                llama, _ = brain.get_llama()
                r = night.run(llama)
                ok_n = r.get("stages_ok", 0)
                total_n = r.get("stages_run", 0)
                elapsed = r.get("elapsed", 0)
                st.markdown(f'<div class="ok-box">Готово: {ok_n}/{total_n} стадий за {elapsed} сек.</div>', unsafe_allow_html=True)
                with st.expander("Подробности"):
                    st.json(r.get("summary", {}))
            except Exception as e:
                st.error(str(e))
    st.markdown('</div>', unsafe_allow_html=True)

    # ---- INGEST ----
    st.markdown('<div class="mod"><div class="mod-title">Ingest</div>', unsafe_allow_html=True)
    st.caption("Файлы из X:\\09_inbox → Chroma")
    if st.button("INGEST INBOX", use_container_width=True, key="btn_ingest"):
        with st.spinner("Ingest..."):
            try:
                ingest_mod.run()
                st.success("Ingest готов")
            except Exception as e:
                st.error(str(e))
    st.markdown('</div>', unsafe_allow_html=True)

    # ---- MEMORY ----
    st.markdown('<div class="mod"><div class="mod-title">Memory</div>', unsafe_allow_html=True)
    try:
        wstats = working.stats()
        st.markdown(f'<div style="font-family:var(--mono);font-size:0.82rem;">active <b>{wstats.get("active", 0)}</b> / total {wstats.get("total", 0)}</div>', unsafe_allow_html=True)
        for k, v in (wstats.get("by_origin") or {}).items():
            st.markdown(f'<span class="pill hot">{k} {v}</span>', unsafe_allow_html=True)
    except Exception as e:
        st.error(str(e))
    st.markdown('</div>', unsafe_allow_html=True)

    # ---- RESET ----
    confirm_reset = st.checkbox("Подтверждаю сброс", key="confirm_reset")
    if st.button("RESET SESSION", use_container_width=True, key="btn_reset", disabled=not confirm_reset):
        brain.storage.reset_session()
        st.success("Сессия сброшена")
        st.rerun()

# ============ CENTER: chat ============
with col_c:
    st.markdown('<div class="mod"><div class="mod-title">Dialog</div>', unsafe_allow_html=True)
    history = brain.get_window()
    for m in history[-12:]:
        with st.chat_message(m["role"]):
            st.write(m["content"])
    st.markdown('</div>', unsafe_allow_html=True)

    if prompt := st.chat_input("> "):
        with st.chat_message("user"):
            st.write(prompt)
        with st.chat_message("assistant"):
            with st.spinner("..."):
                try:
                    r = brain.chat_one(prompt, max_tokens=256)
                    st.write(r["text"])
                    b = r["budget"]
                    st.caption(
                        f"role {b['role_tokens']}/{b['role_cap']} · "
                        f"ret {b['retrieval']['count']}ch/{b['retrieval']['tokens']}t · "
                        f"tps {r['tps']}"
                    )
                    if r.get("compaction", {}).get("triggered"):
                        st.caption("window compacted")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

# ============ RIGHT: reflection ============
with col_r:
    st.markdown('<div class="mod"><div class="mod-title">Reflection</div>', unsafe_allow_html=True)

    # Row of small buttons
    bc1, bc2, bc3 = st.columns(3)
    with bc1:
        if st.button("DIARY", use_container_width=True, key="btn_diary"):
            with st.spinner("diary..."):
                try:
                    llama, _ = brain.get_llama()
                    r = reflect["diary"].run(llama)
                    if r.get("ok"):
                        st.success(f"OK · {r.get('summary_tokens', 0)} tok")
                    else:
                        st.warning(r.get("reason", "no result"))
                except Exception as e:
                    st.error(str(e))
    with bc2:
        if st.button("VOICE", use_container_width=True, key="btn_voice"):
            with st.spinner("voice..."):
                try:
                    llama, _ = brain.get_llama()
                    r = reflect["inner_voice"].run(llama)
                    if r.get("ok"):
                        st.success(f"OK · {r.get('voice_tokens', 0)} tok")
                    else:
                        st.warning(r.get("reason", "no result"))
                except Exception as e:
                    st.error(str(e))
    with bc3:
        if st.button("DREAM", use_container_width=True, key="btn_dream"):
            with st.spinner("dream..."):
                try:
                    llama, _ = brain.get_llama()
                    r = reflect["dream"].run(llama)
                    if r.get("ok"):
                        st.success(f"OK · {r.get('dream_tokens', 0)} tok")
                    else:
                        st.warning(r.get("reason", "no result"))
                except Exception as e:
                    st.error(str(e))

    st.markdown('</div>', unsafe_allow_html=True)

    # Tabs with content
    st.markdown('<div class="mod"><div class="mod-title">Recent</div>', unsafe_allow_html=True)
    t_d, t_v, t_s = st.tabs(["DIARY", "VOICE", "DREAMS"])

    def _render(facts):
        if not facts:
            st.caption("empty")
            return
        for f in facts[-3:]:
            st.markdown(
                f'<div style="border-left:2px solid var(--accent);padding-left:8px;margin-bottom:10px;">'
                f'<div style="font-family:var(--mono);font-size:0.68rem;color:var(--muted);">{f["date"]} · {f["confidence"]}</div>'
                f'<div style="font-size:0.82rem;color:var(--text);margin-top:4px;">{f["text"][:300]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    with t_d:
        _render(working.get_by_origin("diary", days=7))
    with t_v:
        _render(working.get_by_origin("inner_voice", days=7))
    with t_s:
        _render(working.get_by_origin("dream", days=7))
    st.markdown('</div>', unsafe_allow_html=True)
