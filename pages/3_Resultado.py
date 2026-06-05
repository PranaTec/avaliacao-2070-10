import streamlit as st
import pandas as pd
import db
import charts
import layout

st.set_page_config(page_title="Resultado — 20-70-10", page_icon="📊", layout="wide")
empresa = layout.gestor_page()
if not empresa:
    st.stop()

# ── Constantes e helpers ──────────────────────────────────────────────────────

ESCALA = {1: "Não Atende", 2: "Atende Parcialmente",
          3: "Atende Satisfatoriamente", 4: "Supera as Expectativas"}


def _legenda_escala():
    with st.expander("Legenda da escala de notas"):
        for v, label in ESCALA.items():
            st.markdown(f"**{v} — {label}**")


def _tabela_resumo_blocos(respostas: list, mostrar_colaborador: bool):
    blocos: dict = {}
    for r in respostas:
        chave = (r["criterios"]["blocos"]["ordem"], r["criterios"]["blocos"]["nome"])
        if chave not in blocos:
            blocos[chave] = {"n": 0, "pts_g": 0, "pts_c": 0}
        blocos[chave]["n"] += 1
        if r["nota_gestor"]:
            blocos[chave]["pts_g"] += r["nota_gestor"]
        if r["nota_colaborador"]:
            blocos[chave]["pts_c"] += r["nota_colaborador"]

    linhas = []
    for (_, nome), d in sorted(blocos.items()):
        n, pts_g = d["n"], d["pts_g"]
        media_g = round(pts_g / n, 1) if pts_g else 0
        linha = {
            "Bloco": nome,
            "Critérios": n,
            "Máx. possível": n * 4,
            "Pontos gestor": pts_g,
            "Média gestor": f"{media_g} — {ESCALA.get(round(media_g), '')}" if media_g else "—",
        }
        if mostrar_colaborador:
            pts_c = d["pts_c"]
            media_c = round(pts_c / n, 1) if pts_c else 0
            linha["Pontos colaborador"] = pts_c
            linha["Média colaborador"] = f"{media_c} — {ESCALA.get(round(media_c), '')}" if media_c else "—"
        linhas.append(linha)

    st.subheader("Resumo por bloco")
    st.dataframe(pd.DataFrame(linhas), use_container_width=True, hide_index=True)


# ── Carregar avaliação ────────────────────────────────────────────────────────

avaliacao_id = st.session_state.get("avaliacao_id", "")

if not avaliacao_id:
    layout.page_header("Resultado", "Selecione uma avaliação")
    with st.spinner("Carregando avaliações..."):
        todas = db.listar_avaliacoes_empresa(empresa["id"])
    disponiveis = [a for a in todas if a["status"] in ("gestor_ok", "completa")]
    if not disponiveis:
        st.info("Nenhuma avaliação disponível ainda. O gestor precisa preencher pelo menos a parte dele.")
        st.stop()
    for av in disponiveis:
        colab_nome  = av["colaboradores"]["nome"]
        periodo_fmt = f"{av['periodo'][5:]}/{av['periodo'][:4]}"
        status_txt  = "Completa" if av["status"] == "completa" else "Aguardando colaborador"
        if st.button(f"{colab_nome} — {periodo_fmt} — {status_txt}",
                     key=f"sel_{av['id']}", use_container_width=True):
            st.session_state["avaliacao_id"] = av["id"]
            st.rerun()
    st.stop()

with st.spinner("Carregando resultado..."):
    avaliacao = db.buscar_avaliacao_por_id(avaliacao_id)
if not avaliacao or avaliacao["status"] not in ("gestor_ok", "completa"):
    st.warning("Resultado ainda não disponível — o gestor precisa preencher a avaliação primeiro.")
    st.stop()

aguardando_colaborador = avaliacao["status"] == "gestor_ok"
with st.spinner(""):
    respostas    = db.buscar_respostas(avaliacao_id)
colab_nome   = avaliacao["colaboradores"]["nome"]
empresa_nome = avaliacao["empresas"]["nome"]
periodo_fmt  = f"{avaliacao['periodo'][5:]}/{avaliacao['periodo'][:4]}"

layout.page_header("Resultado da Avaliação", colab_nome, f"{empresa_nome} · {periodo_fmt}")
_legenda_escala()

# ── Totais e métricas ─────────────────────────────────────────────────────────

total_g = sum(r["nota_gestor"] for r in respostas if r["nota_gestor"])
n_crit  = len(respostas)
classe_g, cor_g = charts.classificacao(total_g, n_crit)

if aguardando_colaborador:
    st.info("Aguardando a autoavaliação do colaborador para liberar a comparação.")
    st.markdown(f"""
    <div class="metric" style="max-width:220px">
        <div class="metric-label">Avaliação do Gestor</div>
        <div class="metric-value" style="color:{charts.COR_GESTOR}">{total_g}</div>
        <div class="metric-group" style="color:{cor_g}">Grupo {classe_g}</div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    st.subheader("Notas por critério")
    for fig in charts.barras_criterios_gestor(respostas):
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    linhas = []
    for r in sorted(respostas, key=lambda x: (x["criterios"]["blocos"]["ordem"], x["criterios"]["ordem"])):
        ng = r["nota_gestor"]
        linhas.append({
            "Bloco":   r["criterios"]["blocos"]["nome"],
            "Critério": r["criterios"]["nome"],
            "Nota do Gestor": f"{ng} — {ESCALA.get(ng, '')}" if ng else "—",
        })
    st.subheader("Notas registradas")
    st.dataframe(pd.DataFrame(linhas), use_container_width=True, hide_index=True)
    st.divider()
    _tabela_resumo_blocos(respostas, mostrar_colaborador=False)

else:
    total_c = sum(r["nota_colaborador"] for r in respostas if r["nota_colaborador"])
    classe_c, cor_c = charts.classificacao(total_c, n_crit)
    diff  = total_c - total_g
    sinal = "+" if diff > 0 else ""
    cor_diff = "#ef4444" if diff > 2 else "#22c55e" if diff < -2 else "#f59e0b"
    msg   = "Superestima" if diff > 2 else "Subestima" if diff < -2 else "Percepção alinhada"

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""<div class="metric">
            <div class="metric-label">Autoavaliação</div>
            <div class="metric-value" style="color:{charts.COR_COLABORADOR}">{total_c}</div>
            <div class="metric-group" style="color:{cor_c}">Grupo {classe_c}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric">
            <div class="metric-label">Avaliação do Gestor</div>
            <div class="metric-value" style="color:{charts.COR_GESTOR}">{total_g}</div>
            <div class="metric-group" style="color:{cor_g}">Grupo {classe_g}</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric">
            <div class="metric-label">Gap de percepção</div>
            <div class="metric-value" style="color:{cor_diff}">{sinal}{diff}</div>
            <div class="metric-group" style="color:{cor_diff}">{msg}</div>
        </div>""", unsafe_allow_html=True)

    st.divider()
    st.subheader("Diagrama de percepção por bloco")
    st.caption("Área azul = colaborador · Área laranja = gestor. Distância entre elas = gap de percepção.")
    st.plotly_chart(charts.radar_gap(respostas), use_container_width=True)

    st.divider()
    st.subheader("Notas por critério")
    for fig in charts.barras_criterios(respostas):
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("Análise critério a critério")
    linhas = []
    for r in sorted(respostas, key=lambda x: (x["criterios"]["blocos"]["ordem"], x["criterios"]["ordem"])):
        nc, ng = r["nota_colaborador"], r["nota_gestor"]
        media  = round((nc + ng) / 2, 1) if (nc and ng) else None
        gap    = nc - ng if (nc and ng) else None
        gap_txt = "—" if gap is None else ("0 — alinhados" if gap == 0 else
                  f"+{gap} — colaborador se superestima" if gap > 0 else
                  f"{gap} — colaborador se subestima")
        linhas.append({
            "Bloco":        r["criterios"]["blocos"]["nome"],
            "Critério":     r["criterios"]["nome"],
            "Colaborador":  f"{nc} — {ESCALA.get(nc, '')}" if nc else "—",
            "Gestor":       f"{ng} — {ESCALA.get(ng, '')}" if ng else "—",
            "Média":        f"{media} — {ESCALA.get(round(media), '')}" if media else "—",
            "Gap":          gap_txt,
        })
    st.dataframe(pd.DataFrame(linhas), use_container_width=True, hide_index=True)
    st.divider()
    _tabela_resumo_blocos(respostas, mostrar_colaborador=True)

# ── Observações ───────────────────────────────────────────────────────────────

st.divider()
st.subheader("Pontos de melhoria")
obs_atual = avaliacao.get("observacoes") or ""

if obs_atual:
    st.markdown(f"""<div class="obs-box">
        <div class="obs-label">Registrado pelo Gestor</div>
        <div class="obs-text">{obs_atual}</div>
    </div>""", unsafe_allow_html=True)

with st.expander("Editar observações"):
    obs_nova = st.text_area("", value=obs_atual, height=150,
                            placeholder="Registre pontos de desenvolvimento para o próximo período...",
                            label_visibility="collapsed")
    if st.button("Salvar", type="primary", key="_obs_save"):
        db.salvar_observacoes(avaliacao_id, obs_nova.strip())
        st.success("Observações salvas!")
        st.rerun()

st.divider()
if st.button("Ver histórico deste colaborador", type="primary"):
    st.session_state["colaborador_id"] = avaliacao["colaborador_id"]
    st.switch_page("pages/4_Historico.py")
