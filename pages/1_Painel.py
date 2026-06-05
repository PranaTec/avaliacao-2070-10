import streamlit as st
import db
import layout
from datetime import date

st.set_page_config(page_title="Painel — 20-70-10", page_icon="📊", layout="wide")
empresa = layout.gestor_page()
if not empresa:
    st.stop()

layout.page_header("Painel de Gestão", empresa["nome"])

abas = st.tabs(["Avaliações do mês", "Colaboradores", "Configurações dos critérios"])

# ══════════════════════════════════════════════════════════════════════════════
# ABA 1 — Avaliações
# ══════════════════════════════════════════════════════════════════════════════
with abas[0]:
    # ── Seletor de período ────────────────────────────────────────────────────
    hoje = date.today()
    opcoes = {}
    for i in range(11, -1, -1):
        mes = hoje.month - i
        ano = hoje.year
        while mes <= 0:
            mes += 12
            ano -= 1
        opcoes[f"{mes:02d}/{ano}"] = f"{ano}-{mes:02d}"

    # ── Nova avaliação ────────────────────────────────────────────────────────
    colaboradores = db.listar_colaboradores(empresa["id"])
    st.markdown("### Nova avaliação")

    if not colaboradores:
        st.warning("Cadastre ao menos um colaborador antes de iniciar uma avaliação.")
        periodo = opcoes[list(opcoes.keys())[-1]]
    else:
        nomes = {c["nome"]: c["id"] for c in colaboradores}
        col_colab, col_mes, col_btn = st.columns([3, 2, 2])
        with col_colab:
            nome_sel = st.selectbox("Colaborador", list(nomes.keys()), key="sel_colab_nova", label_visibility="visible")
        with col_mes:
            sel = st.selectbox("Período", list(opcoes.keys()), index=len(opcoes) - 1)
            periodo = opcoes[sel]
        with col_btn:
            st.markdown("<div style='padding-top:1.75rem'>", unsafe_allow_html=True)
            gerar = st.button("Gerar avaliação", type="primary", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        if gerar:
            existente = db.buscar_avaliacao_existente(nomes[nome_sel], empresa["id"], periodo)
            if existente:
                st.warning(f"Já existe uma avaliação para **{nome_sel}** em **{sel}**. Exibindo a existente.")
                st.session_state["nova_avaliacao"] = existente
            else:
                av = db.criar_avaliacao(nomes[nome_sel], empresa["id"], periodo)
                st.session_state["nova_avaliacao"] = av
            st.rerun()

    if "nova_avaliacao" in st.session_state:
        av = st.session_state["nova_avaliacao"]
        st.success("Links gerados! Envie cada um para a pessoa certa.")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Código do Colaborador**")
            st.code(av["token_colaborador"])
            st.caption("O colaborador usa esse código na tela inicial para preencher a autoavaliação.")
        with c2:
            st.markdown("**Código do Gestor**")
            st.code(av["token_gestor"])
            st.caption("Você usa esse código para preencher a avaliação como gestor.")
        if st.button("Fechar"):
            del st.session_state["nova_avaliacao"]
            st.rerun()

    st.divider()
    st.markdown("### Avaliações registradas")
    avaliacoes = db.listar_avaliacoes_empresa(empresa["id"])
    avaliacoes_periodo = [a for a in avaliacoes if a["periodo"] == periodo]

    STATUS_LABEL = {
        "pendente":       "Aguardando ambos",
        "colaborador_ok": "Colaborador preencheu — aguardando gestor",
        "gestor_ok":      "Gestor preencheu — aguardando colaborador",
        "completa":       "Completa",
    }

    if not avaliacoes_periodo:
        st.info("Nenhuma avaliação iniciada para este período.")
    else:
        for av in avaliacoes_periodo:
            colab_nome = av["colaboradores"]["nome"]
            status_txt = STATUS_LABEL.get(av["status"], av["status"])
            with st.expander(f"{colab_nome} — {status_txt}"):
                if av["status"] in ("gestor_ok", "completa"):
                    if st.button(f"Ver resultado", key=f"res_{av['id']}", type="primary"):
                        st.session_state["avaliacao_id"] = av["id"]
                        st.switch_page("pages/3_Resultado.py")
                if av["status"] == "completa":
                    if st.button(f"Ver histórico", key=f"hist_{av['id']}"):
                        st.session_state["colaborador_id"] = av["colaborador_id"]
                        st.switch_page("pages/4_Historico.py")
                if av["status"] not in ("gestor_ok", "completa"):
                    if st.button("Preencher como Gestor", key=f"fill_{av['id']}", type="primary"):
                        st.session_state["token_form"] = av["token_gestor"]
                        st.session_state["tipo_form"] = "gestor"
                        st.switch_page("pages/2_Avaliar.py")
                    st.divider()
                    c_tok1, c_tok2 = st.columns(2)
                    with c_tok1:
                        st.caption("Código do colaborador")
                        st.code(av["token_colaborador"], language=None)
                    with c_tok2:
                        st.caption("Código do gestor")
                        st.code(av["token_gestor"], language=None)

# ══════════════════════════════════════════════════════════════════════════════
# ABA 2 — Colaboradores
# ══════════════════════════════════════════════════════════════════════════════
with abas[1]:
    st.markdown("### Cadastrar colaborador")
    with st.form("form_colab"):
        nome_c = st.text_input("Nome completo")
        funcao_c = st.text_input("Função / Cargo")
        admissao_c = st.date_input("Data de admissão", value=None)
        sub_c = st.form_submit_button("Cadastrar", type="primary")

    if sub_c:
        if nome_c.strip() and funcao_c.strip():
            db.criar_colaborador(empresa["id"], nome_c.strip(), funcao_c.strip(),
                                 admissao_c.isoformat() if admissao_c else None)
            st.success(f"{nome_c} cadastrado com sucesso!")
            st.rerun()
        else:
            st.error("Nome e função são obrigatórios.")

    st.divider()
    st.markdown("### Colaboradores ativos")
    colaboradores = db.listar_colaboradores(empresa["id"])
    if not colaboradores:
        st.info("Nenhum colaborador cadastrado ainda.")
    else:
        for c in colaboradores:
            with st.expander(f"{c['nome']} — {c['funcao']}"):
                with st.form(f"edit_{c['id']}"):
                    nome_e = st.text_input("Nome", value=c["nome"])
                    funcao_e = st.text_input("Função / Cargo", value=c["funcao"])
                    admissao_val = None
                    if c.get("data_admissao"):
                        admissao_val = date.fromisoformat(c["data_admissao"][:10])
                    admissao_e = st.date_input("Data de admissão", value=admissao_val)
                    col_s, col_r = st.columns(2)
                    with col_s:
                        salvar = st.form_submit_button("Salvar", type="primary", use_container_width=True)
                    with col_r:
                        remover = st.form_submit_button("Desativar", use_container_width=True)

                if salvar:
                    if nome_e.strip() and funcao_e.strip():
                        db.atualizar_colaborador(c["id"], nome_e.strip(), funcao_e.strip(),
                                                 admissao_e.isoformat() if admissao_e else None)
                        st.success("Atualizado!")
                        st.rerun()
                    else:
                        st.error("Nome e função são obrigatórios.")
                if remover:
                    db.desativar_colaborador(c["id"])
                    st.warning(f"{c['nome']} desativado.")
                    st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# ABA 3 — Critérios
# ══════════════════════════════════════════════════════════════════════════════
with abas[2]:
    st.markdown("### Editar critérios de avaliação")
    st.caption("Alterações afetam apenas novas avaliações. Avaliações já criadas não são modificadas.")

    blocos = db.listar_blocos_com_criterios(empresa["id"])
    for bloco in blocos:
        st.markdown(f"#### {bloco['nome']}")
        for crit in bloco["criterios"]:
            with st.expander(crit["nome"]):
                novo_nome = st.text_input("Nome", value=crit["nome"], key=f"nome_{crit['id']}")
                nova_desc = st.text_input("Descrição", value=crit["descricao"] or "", key=f"desc_{crit['id']}")
                col_s, col_r = st.columns(2)
                with col_s:
                    if st.button("Salvar", key=f"salvar_{crit['id']}"):
                        db.atualizar_criterio(crit["id"], novo_nome, nova_desc)
                        st.success("Salvo!")
                        st.rerun()
                with col_r:
                    if st.button("Remover", key=f"rem_{crit['id']}", type="secondary"):
                        db.remover_criterio(crit["id"])
                        st.warning("Critério removido.")
                        st.rerun()

        with st.expander(f"+ Adicionar critério em {bloco['nome']}"):
            with st.form(f"add_{bloco['id']}"):
                novo_c_nome = st.text_input("Nome do critério")
                novo_c_desc = st.text_input("Descrição")
                if st.form_submit_button("Adicionar"):
                    if novo_c_nome.strip():
                        db.adicionar_criterio(bloco["id"], empresa["id"], novo_c_nome.strip(),
                                              novo_c_desc.strip(), len(bloco["criterios"]) + 1)
                        st.success("Critério adicionado!")
                        st.rerun()
