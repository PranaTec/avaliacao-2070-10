import streamlit as st
import layout

st.set_page_config(
    page_title="Avaliação 20-70-10",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed",
)
layout.public_page()

st.markdown('<p style="font-size:0.72rem;font-weight:700;letter-spacing:0.14em;text-transform:uppercase;color:#3b82f6;margin-bottom:0.3rem">Sistema de Avaliação</p>', unsafe_allow_html=True)
st.title("Avaliação 20-70-10")
st.markdown('<p class="page-sub">Desenvolvimento contínuo de colaboradores com base em percepção e resultado.</p>', unsafe_allow_html=True)

st.divider()

col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("""
    <div class="home-card">
        <div class="home-card-tag">Gestão</div>
        <div class="home-card-title">Sou Gestor</div>
        <div class="home-card-desc">Acesse o painel da sua empresa para gerenciar avaliações e acompanhar resultados.</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
    token_empresa = st.text_input("Código da empresa", key="inp_empresa", placeholder="Cole o código aqui", label_visibility="collapsed")
    if st.button("Entrar como Gestor", use_container_width=True, type="primary"):
        if token_empresa.strip():
            st.session_state["token_empresa"] = token_empresa.strip()
            st.switch_page("pages/1_Painel.py")
        else:
            st.error("Digite o código da empresa.")

with col2:
    st.markdown("""
    <div class="home-card">
        <div class="home-card-tag">Colaborador</div>
        <div class="home-card-title">Sou Colaborador</div>
        <div class="home-card-desc">Recebeu um código de avaliação? Cole aqui para preencher sua autoavaliação.</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
    token_colab = st.text_input("Código da avaliação", key="token_colab", placeholder="Cole o código aqui", label_visibility="collapsed")
    if st.button("Preencher avaliação", use_container_width=True, type="primary"):
        if token_colab.strip():
            st.session_state["token_form"] = token_colab.strip()
            st.session_state["tipo_form"] = "colaborador"
            st.switch_page("pages/2_Avaliar.py")
        else:
            st.error("Digite o código recebido.")

st.divider()
st.markdown('<p class="page-sub" style="text-align:center">Primeira vez? <a href="#" style="color:#3b82f6">Cadastre sua empresa</a> para começar.</p>', unsafe_allow_html=True)
if st.button("Cadastrar nova empresa", use_container_width=False):
    st.switch_page("pages/5_Nova_Empresa.py")
