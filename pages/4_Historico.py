import streamlit as st
import pandas as pd
import db
import charts
import layout

st.set_page_config(page_title="Histórico — 20-70-10", page_icon="📊", layout="centered")
empresa = layout.gestor_page()
if not empresa:
    st.stop()

colaborador_id = st.session_state.get("colaborador_id", "")

if not colaborador_id:
    layout.page_header("Histórico", "Histórico de avaliações",
                       "Selecione o colaborador para ver a evolução ao longo do tempo.")
    colaboradores = db.listar_colaboradores(empresa["id"])
    if not colaboradores:
        st.info("Nenhum colaborador cadastrado ainda.")
        st.stop()
    nomes = {c["nome"]: c["id"] for c in colaboradores}
    sel = st.selectbox("Colaborador", list(nomes.keys()))
    if st.button("Ver histórico", type="primary"):
        st.session_state["colaborador_id"] = nomes[sel]
        st.rerun()
    st.stop()

with st.spinner("Carregando histórico..."):
    colab     = db.buscar_colaborador_por_id(colaborador_id)
    historico = db.historico_colaborador(colaborador_id)
nome = colab["nome"] if colab else "Colaborador"

col_title, col_trocar = st.columns([5, 1])
with col_title:
    layout.page_header("Histórico", nome, "Evolução das avaliações ao longo do tempo.")
with col_trocar:
    st.markdown("<div style='padding-top:1.6rem'>", unsafe_allow_html=True)
    if st.button("Trocar", use_container_width=True):
        st.session_state.pop("colaborador_id", None)
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

if not historico:
    st.info("Ainda não há avaliações completas registradas para este colaborador.")
    st.stop()

fig = charts.linha_historico(historico)
if fig:
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.subheader("Histórico de pontuações")

linhas = []
for h in historico:
    n_crit = 16
    classe_c, _ = charts.classificacao(h["total_colaborador"], n_crit)
    classe_g, _ = charts.classificacao(h["total_gestor"], n_crit)
    p = h["periodo"]
    linhas.append({
        "Período":      f"{p[5:]}/{p[:4]}",
        "Autoavaliação": h["total_colaborador"],
        "Grupo (auto)": classe_c,
        "Gestor":       h["total_gestor"],
        "Grupo (gestor)": classe_g,
        "Gap":          h["total_colaborador"] - h["total_gestor"],
    })

st.dataframe(pd.DataFrame(linhas), use_container_width=True, hide_index=True)
