import streamlit as st
import db
import layout

st.set_page_config(page_title="Nova Empresa — 20-70-10", page_icon="📊", layout="centered")
layout.public_page()

st.markdown('<p style="font-size:0.72rem;font-weight:700;letter-spacing:0.14em;text-transform:uppercase;color:#3b82f6;margin-bottom:0.3rem">Cadastro</p>', unsafe_allow_html=True)
st.title("Nova empresa")
st.markdown('<p class="page-sub">Após o cadastro você receberá um código único para acessar o painel de gestão.</p>', unsafe_allow_html=True)
st.divider()

with st.form("form_empresa"):
    nome = st.text_input("Nome da empresa", placeholder="Ex: Prana Consultoria")
    submitted = st.form_submit_button("Cadastrar empresa", type="primary", use_container_width=True)

if submitted:
    if not nome.strip():
        st.error("O nome da empresa é obrigatório.")
    else:
        with st.spinner("Cadastrando..."):
            empresa = db.criar_empresa(nome.strip())
        st.success(f"Empresa **{empresa['nome']}** cadastrada!")
        st.markdown(f"""
        <div class="obs-box" style="border-color:#1e3a5f;background:#12203a;">
            <div class="obs-label" style="color:#93c5fd">Código de acesso — guarde com segurança</div>
            <div class="obs-text" style="color:#e2e8f0;font-family:monospace;font-size:1rem">{empresa['token_gestor']}</div>
        </div>
        """, unsafe_allow_html=True)
        st.session_state["token_empresa"] = empresa["token_gestor"]
        st.switch_page("pages/1_Painel.py")
