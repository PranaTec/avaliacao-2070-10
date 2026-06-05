import streamlit as st

CSS = """
<style>
/* ── Reset ─────────────────────────────────────────────── */
#MainMenu, footer { visibility: hidden; }

/* ── Tipografia ─────────────────────────────────────────── */
h1 { font-size:1.55rem!important; font-weight:700!important;
     letter-spacing:-0.02em!important; color:#f1f5f9!important; margin-bottom:0.15rem!important; }
h2 { font-size:1.1rem!important; font-weight:600!important; color:#e2e8f0!important; }
h3 { font-size:0.95rem!important; font-weight:600!important; color:#e2e8f0!important; }
hr { border-color:#252d3d!important; margin:1.5rem 0!important; }

/* ── Cards ──────────────────────────────────────────────── */
.card {
    background:#161b27; border:1px solid #252d3d;
    border-radius:10px; padding:1.4rem 1.6rem; margin-bottom:0.75rem;
}

/* ── Métricas ───────────────────────────────────────────── */
.metric {
    background:#161b27; border:1px solid #252d3d;
    border-radius:10px; padding:1.2rem 1.5rem; text-align:center;
}
.metric-label { font-size:0.72rem; color:#64748b;
    text-transform:uppercase; letter-spacing:0.1em; }
.metric-value { font-size:2.4rem; font-weight:800; line-height:1.1; margin:0.2rem 0; }
.metric-group { font-size:0.88rem; font-weight:600; color:#94a3b8; }

/* ── Cabeçalho de bloco ─────────────────────────────────── */
.bloco-header {
    padding:0.4rem 0; margin:2rem 0 0.7rem;
    border-bottom:1px solid #252d3d;
}
.bloco-header span {
    font-size:0.7rem; font-weight:800;
    letter-spacing:0.14em; text-transform:uppercase; color:#3b82f6;
}

/* ── Card de critério ───────────────────────────────────── */
.criterio-card {
    background:#0e1118; border:1px solid #252d3d;
    border-left:3px solid #3b82f6; border-radius:8px;
    padding:0.85rem 1.1rem 0.25rem; margin-bottom:0.45rem;
}
.criterio-nome { font-size:0.93rem; font-weight:600; color:#e2e8f0; margin-bottom:0.1rem; }
.criterio-desc { font-size:0.79rem; color:#64748b; line-height:1.4; margin-bottom:0.4rem; }

/* ── Box instrução ──────────────────────────────────────── */
.instrucao-box {
    background:#12203a; border:1px solid #1e3a5f;
    border-left:4px solid #3b82f6; padding:1rem 1.3rem;
    border-radius:8px; margin-bottom:1.5rem;
    color:#cbd5e1; font-size:0.91rem; line-height:1.7;
}
.instrucao-box strong { color:#93c5fd; }

/* ── Box observações ────────────────────────────────────── */
.obs-box {
    background:#0a1a0a; border:1px solid #14532d;
    border-left:4px solid #22c55e; padding:1rem 1.2rem;
    border-radius:8px; margin-bottom:0.8rem;
}
.obs-label { font-size:0.68rem; font-weight:700; letter-spacing:0.12em;
    text-transform:uppercase; color:#4ade80; margin-bottom:0.4rem; }
.obs-text { color:#bbf7d0; font-size:0.91rem; line-height:1.6; white-space:pre-wrap; }

/* ── Cards da home ──────────────────────────────────────── */
.home-card {
    background:#161b27; border:1px solid #252d3d;
    border-radius:12px; padding:1.8rem 1.6rem;
}
.home-card-tag {
    font-size:0.68rem; font-weight:700; letter-spacing:0.12em;
    text-transform:uppercase; color:#3b82f6; margin-bottom:0.6rem;
}
.home-card-title { font-size:1.1rem; font-weight:700; color:#f1f5f9; margin-bottom:0.35rem; }
.home-card-desc { font-size:0.84rem; color:#64748b; line-height:1.5; margin-bottom:1.2rem; }

/* ── Label de seção ─────────────────────────────────────── */
.section-label {
    font-size:0.68rem; font-weight:700; letter-spacing:0.12em;
    text-transform:uppercase; color:#64748b; margin-bottom:0.5rem;
}

/* ── Subtítulo de página ────────────────────────────────── */
.page-sub { font-size:0.84rem; color:#64748b; margin-top:-0.3rem; margin-bottom:1.4rem; }

/* ── Token box ──────────────────────────────────────────── */
.token-box {
    background:#0e1118; border:1px solid #252d3d; border-radius:7px;
    padding:0.7rem 1rem; font-family:monospace; font-size:0.88rem;
    color:#93c5fd; letter-spacing:0.04em; word-break:break-all;
}

/* ── Streamlit overrides ────────────────────────────────── */
div[data-testid="stRadio"] > label:first-child { display:none; }
div[data-testid="stExpander"] {
    border:1px solid #252d3d!important; border-radius:8px!important;
    background:#161b27!important;
}
section[data-testid="stSidebar"] { display:none!important; }

/* Botão primário → azul (todos os tipos) */
.stButton > button,
div[data-testid="stFormSubmitButton"] > button {
    border-radius:7px!important; font-weight:600!important;
}
.stButton > button[kind="primary"],
div[data-testid="stFormSubmitButton"] > button[kind="primaryFormSubmit"],
div[data-testid="stFormSubmitButton"] > button {
    background-color:#2563eb!important;
    border-color:#2563eb!important;
    color:#fff!important;
}
.stButton > button[kind="primary"]:hover,
div[data-testid="stFormSubmitButton"] > button:hover {
    background-color:#1d4ed8!important;
    border-color:#1d4ed8!important;
}

.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background:#0e1118!important; border:1px solid #252d3d!important;
    border-radius:7px!important; color:#f1f5f9!important;
}
.stDataFrame { border-radius:8px!important; overflow:hidden!important; }
.stTabs [data-baseweb="tab"] { font-weight:500!important; }
.stTabs [data-baseweb="tab-list"] { background:#161b27!important;
    border-radius:8px 8px 0 0!important; padding:0 0.5rem!important; }
</style>
"""

NAV_CSS = """
<style>
.nav-wrap {
    display:flex; align-items:center; gap:0.25rem;
    padding:0.5rem 0; margin-bottom:1rem;
    border-bottom:1px solid #252d3d;
}
/* page_link: estado normal */
div[data-testid="stPageLink"] a {
    color:#64748b!important; font-size:0.85rem!important;
    font-weight:500!important; text-decoration:none!important;
    padding:0.3rem 0.75rem!important; border-radius:6px!important;
    display:block!important;
}
div[data-testid="stPageLink"] a:hover {
    color:#f1f5f9!important; background:#1e2535!important;
}
/* page_link: página atual */
div[data-testid="stPageLink"] a[aria-current="page"] {
    color:#3b82f6!important; font-weight:700!important;
    background:#162033!important;
}
/* botão Sair na nav */
.nav-sair button {
    background:transparent!important; border:none!important;
    color:#64748b!important; font-size:0.85rem!important;
    font-weight:500!important; padding:0.3rem 0.75rem!important;
    height:auto!important;
}
.nav-sair button:hover { color:#f1f5f9!important; background:#1e2535!important; }
</style>
"""

def apply():
    st.markdown(CSS, unsafe_allow_html=True)


def navbar():
    """Barra de navegação superior — apenas para páginas do gestor."""
    st.markdown(NAV_CSS, unsafe_allow_html=True)
    st.markdown('<div class="nav-wrap">', unsafe_allow_html=True)
    c1, c2, c3, gap, c4 = st.columns([1.2, 1.3, 1.3, 4, 1.4])
    with c1:
        st.page_link("pages/1_Painel.py", label="Painel")
    with c2:
        st.page_link("pages/3_Resultado.py", label="Resultado")
    with c3:
        st.page_link("pages/4_Historico.py", label="Histórico")
    with c4:
        st.markdown('<div class="nav-sair">', unsafe_allow_html=True)
        if st.button("Sair", key="nav_sair_btn"):
            for k in ["token_empresa", "empresa_id", "avaliacao_id", "colaborador_id"]:
                st.session_state.pop(k, None)
            st.switch_page("app.py")
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
