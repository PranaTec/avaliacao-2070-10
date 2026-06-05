import streamlit as st
import db
import layout

st.set_page_config(page_title="Avaliação — 20-70-10", page_icon="📊", layout="centered")
avaliacao, tipo = layout.colaborador_page()
if not avaliacao:
    st.stop()

# Tokens still in session state for post-submit use
token = st.session_state.get("token_form", "")

status = avaliacao["status"]
ja_preencheu = (tipo == "colaborador" and status in ("colaborador_ok", "completa")) or \
               (tipo == "gestor" and status in ("gestor_ok", "completa"))

colab_nome  = avaliacao["colaboradores"]["nome"]
colab_func  = avaliacao["colaboradores"]["funcao"]
empresa_nome = avaliacao["empresas"]["nome"]
periodo     = avaliacao["periodo"]
periodo_fmt = f"{periodo[5:]}/{periodo[:4]}"

tag = "Autoavaliação" if tipo == "colaborador" else "Avaliação do Gestor"
layout.page_header(tag, colab_nome, f"{empresa_nome} · {colab_func} · {periodo_fmt}")

if ja_preencheu:
    st.success("Você já preencheu esta avaliação. Obrigado!")
    if status == "completa":
        st.info("Ambas as partes já preencheram. O resultado está disponível para o gestor.")
    else:
        st.info("Aguardando a outra parte preencher para liberar o resultado.")
    st.stop()

# ── Instruções ────────────────────────────────────────────────────────────────
if tipo == "colaborador":
    st.markdown("""
<div class="instrucao-box">
<strong>Como preencher:</strong><br><br>
Avalie a si mesmo em cada critério usando a escala de 1 a 4:<br><br>
&nbsp;&nbsp;<strong>1 — Não Atende:</strong> Fico abaixo do esperado neste quesito.<br>
&nbsp;&nbsp;<strong>2 — Atende Parcialmente:</strong> Estou em desenvolvimento, mas ainda não atingi o esperado.<br>
&nbsp;&nbsp;<strong>3 — Atende Satisfatoriamente:</strong> Cumpro o que é esperado de forma consistente.<br>
&nbsp;&nbsp;<strong>4 — Supera as Expectativas:</strong> Entrego acima do esperado com frequência.<br><br>
Seja honesto — esta avaliação é uma ferramenta de crescimento, não de julgamento.
</div>
""", unsafe_allow_html=True)
else:
    st.markdown(f"""
<div class="instrucao-box">
<strong>Como preencher:</strong><br><br>
Avalie <strong>{colab_nome}</strong> em cada critério usando a escala de 1 a 4:<br><br>
&nbsp;&nbsp;<strong>1 — Não Atende:</strong> O colaborador fica abaixo do esperado neste quesito.<br>
&nbsp;&nbsp;<strong>2 — Atende Parcialmente:</strong> Está em desenvolvimento, mas ainda não atingiu o esperado.<br>
&nbsp;&nbsp;<strong>3 — Atende Satisfatoriamente:</strong> Cumpre o que é esperado de forma consistente.<br>
&nbsp;&nbsp;<strong>4 — Supera as Expectativas:</strong> Entrega acima do esperado com frequência.<br><br>
Avalie com base em comportamentos observados no período <strong>{periodo_fmt}</strong>.
</div>
""", unsafe_allow_html=True)

# ── Formulário ────────────────────────────────────────────────────────────────
respostas_raw = db.buscar_respostas(avaliacao["id"])

respostas_por_bloco: dict[str, list] = {}
for r in respostas_raw:
    chave = f"{r['criterios']['blocos']['ordem']}|{r['criterios']['blocos']['nome']}"
    respostas_por_bloco.setdefault(chave, []).append(r)

ESCALA_LABELS = [
    "1 — Não Atende",
    "2 — Atende Parcialmente",
    "3 — Atende Satisfatoriamente",
    "4 — Supera as Expectativas",
]
ESCALA_VALS = [1, 2, 3, 4]

notas_coletadas: dict[str, int] = {}
criterios_em_branco: list[str] = []

with st.form("form_avaliacao"):
    for chave in sorted(respostas_por_bloco.keys()):
        _, bloco_nome = chave.split("|", 1)
        respostas_bloco = sorted(respostas_por_bloco[chave], key=lambda x: x["criterios"]["ordem"])

        st.markdown(f'<div class="bloco-header"><span>▎ {bloco_nome}</span></div>', unsafe_allow_html=True)

        for resp in respostas_bloco:
            crit = resp["criterios"]
            desc_html = f'<div class="criterio-desc">{crit["descricao"]}</div>' if crit.get("descricao") else ""
            st.markdown(
                f'<div class="criterio-card">'
                f'<div class="criterio-nome">{crit["nome"]}</div>'
                f'{desc_html}'
                f'</div>',
                unsafe_allow_html=True,
            )
            opcao = st.radio(
                label=crit["nome"],
                options=ESCALA_VALS,
                format_func=lambda v: ESCALA_LABELS[v - 1],
                index=None,
                key=f"nota_{resp['criterio_id']}",
                label_visibility="collapsed",
                horizontal=False,
            )
            notas_coletadas[resp["criterio_id"]] = opcao
            if opcao is None:
                criterios_em_branco.append(f"{bloco_nome} → {crit['nome']}")

    enviado = st.form_submit_button("Enviar avaliação", type="primary", use_container_width=True)

if enviado:
    if criterios_em_branco:
        itens = "\n".join(f"- {c}" for c in criterios_em_branco)
        st.error(f"Faltam {len(criterios_em_branco)} critério(s) sem resposta:\n\n{itens}")
    else:
        with st.spinner("Salvando..."):
            if tipo == "colaborador":
                db.salvar_respostas_colaborador(avaliacao["id"], notas_coletadas)
            else:
                db.salvar_respostas_gestor(avaliacao["id"], notas_coletadas)

        avaliacao_atualizada = db.buscar_avaliacao_por_token(token, tipo)

        if tipo == "gestor":
            st.session_state["avaliacao_id"] = avaliacao_atualizada["id"]
            st.session_state.pop("token_form", None)
            st.session_state.pop("tipo_form", None)
            st.switch_page("pages/3_Resultado.py")
        else:
            st.session_state.pop("token_form", None)
            st.session_state.pop("tipo_form", None)
            st.markdown(f"""
<div class="instrucao-box">
<strong>Obrigado, {colab_nome}!</strong><br><br>
Sua autoavaliação foi registrada com sucesso.<br><br>
A partir de agora, seu gestor irá analisar as respostas e comparar com a avaliação dele.
Com base nisso, será agendada uma <strong>sessão de feedback</strong> para conversarem sobre
os resultados, alinhar percepções e definir juntos os próximos passos do seu desenvolvimento.<br><br>
Fique à vontade para fechar esta página.
</div>
""", unsafe_allow_html=True)
            if st.button("Preencher outra avaliação"):
                st.rerun()
