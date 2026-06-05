import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


ESCALA = {1: "Não Atende", 2: "Atende Parcialmente", 3: "Atende Satisfatoriamente", 4: "Supera as Expectativas"}

COR_COLABORADOR = "#4F86C6"
COR_GESTOR = "#F4845F"


def classificacao(total: int, n_criterios: int) -> tuple[str, str]:
    max_score = n_criterios * 4
    pct = total / max_score if max_score > 0 else 0
    if pct < 0.30:
        return "10%", "#E74C3C"
    elif pct < 0.88:
        return "70%", "#F39C12"
    else:
        return "20%", "#27AE60"


def radar_gap(respostas: list) -> go.Figure:
    blocos = {}
    for r in respostas:
        bloco_nome = r["criterios"]["blocos"]["nome"]
        if bloco_nome not in blocos:
            blocos[bloco_nome] = {"colaborador": [], "gestor": []}
        if r["nota_colaborador"]:
            blocos[bloco_nome]["colaborador"].append(r["nota_colaborador"])
        if r["nota_gestor"]:
            blocos[bloco_nome]["gestor"].append(r["nota_gestor"])

    categorias = list(blocos.keys())
    medias_c = [sum(v["colaborador"]) / len(v["colaborador"]) if v["colaborador"] else 0 for v in blocos.values()]
    medias_g = [sum(v["gestor"]) / len(v["gestor"]) if v["gestor"] else 0 for v in blocos.values()]

    categorias_fechadas = categorias + [categorias[0]]
    medias_c_fechadas = medias_c + [medias_c[0]]
    medias_g_fechadas = medias_g + [medias_g[0]]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=medias_c_fechadas,
        theta=categorias_fechadas,
        fill="toself",
        name="Colaborador",
        line=dict(color=COR_COLABORADOR, width=2),
        fillcolor=f"rgba(79, 134, 198, 0.25)",
    ))

    fig.add_trace(go.Scatterpolar(
        r=medias_g_fechadas,
        theta=categorias_fechadas,
        fill="toself",
        name="Gestor",
        line=dict(color=COR_GESTOR, width=2),
        fillcolor=f"rgba(244, 132, 95, 0.25)",
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 4], tickvals=[1, 2, 3, 4], ticktext=["1", "2", "3", "4"]),
            bgcolor="#FAFAFA",
        ),
        showlegend=True,
        legend=dict(orientation="h", y=-0.15),
        margin=dict(t=40, b=60, l=60, r=60),
        height=420,
        font=dict(family="Inter, sans-serif"),
    )
    return fig


def barras_criterios(respostas: list) -> go.Figure:
    blocos_ordem = {}
    for r in respostas:
        bloco = r["criterios"]["blocos"]["nome"]
        bloco_ord = r["criterios"]["blocos"]["ordem"]
        criterio = r["criterios"]["nome"]
        descricao = r["criterios"].get("descricao") or ""
        nc = r["nota_colaborador"] or 0
        ng = r["nota_gestor"] or 0
        if bloco not in blocos_ordem:
            blocos_ordem[bloco] = {"ordem": bloco_ord, "linhas": []}
        blocos_ordem[bloco]["linhas"].append({
            "criterio": criterio,
            "descricao": descricao,
            "colaborador": nc,
            "gestor": ng,
        })

    blocos_sorted = sorted(blocos_ordem.items(), key=lambda x: x[1]["ordem"])

    figs = []
    for bloco_nome, dados in blocos_sorted:
        linhas = dados["linhas"]
        criterios  = [l["criterio"]  for l in linhas]
        descricoes = [l["descricao"] for l in linhas]
        vals_c = [l["colaborador"] for l in linhas]
        vals_g = [l["gestor"]      for l in linhas]

        notas_validas = [v for v in vals_c + vals_g if v > 0]
        media_bloco = round(sum(notas_validas) / len(notas_validas), 1) if notas_validas else 0
        media_label = ESCALA.get(round(media_bloco), "")

        HOVER = "<b>%{x}</b><br><i>%{customdata}</i><br>Nota: <b>%{y}</b><extra></extra>"
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Colaborador", x=criterios, y=vals_c,
                             marker_color=COR_COLABORADOR,
                             customdata=descricoes, hovertemplate=HOVER))
        fig.add_trace(go.Bar(name="Gestor", x=criterios, y=vals_g,
                             marker_color=COR_GESTOR,
                             customdata=descricoes, hovertemplate=HOVER))
        fig.update_layout(
            title=dict(
                text=f"{bloco_nome}<br><sup>Média do bloco: {media_bloco} — {media_label}</sup>" if media_bloco else bloco_nome,
                font=dict(size=15),
            ),
            barmode="group",
            yaxis=dict(range=[0, 4.5], tickvals=[1, 2, 3, 4]),
            legend=dict(orientation="h", y=-0.25),
            height=320,
            margin=dict(t=60, b=60, l=40, r=20),
            font=dict(family="Inter, sans-serif"),
        )
        figs.append(fig)
    return figs


def barras_criterios_gestor(respostas: list) -> list:
    blocos_ordem = {}
    for r in respostas:
        bloco = r["criterios"]["blocos"]["nome"]
        bloco_ord = r["criterios"]["blocos"]["ordem"]
        criterio = r["criterios"]["nome"]
        descricao = r["criterios"].get("descricao") or ""
        ng = r["nota_gestor"] or 0
        if bloco not in blocos_ordem:
            blocos_ordem[bloco] = {"ordem": bloco_ord, "linhas": []}
        blocos_ordem[bloco]["linhas"].append({"criterio": criterio, "descricao": descricao, "gestor": ng})

    figs = []
    for bloco_nome, dados in sorted(blocos_ordem.items(), key=lambda x: x[1]["ordem"]):
        linhas = dados["linhas"]
        criterios  = [l["criterio"]  for l in linhas]
        descricoes = [l["descricao"] for l in linhas]
        vals_g = [l["gestor"] for l in linhas]
        notas_validas_g = [v for v in vals_g if v > 0]
        media_bloco = round(sum(notas_validas_g) / len(notas_validas_g), 1) if notas_validas_g else 0
        media_label = ESCALA.get(round(media_bloco), "")

        HOVER = "<b>%{x}</b><br><i>%{customdata}</i><br>Nota: <b>%{y}</b><extra></extra>"
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Gestor", x=criterios, y=vals_g,
                             marker_color=COR_GESTOR,
                             customdata=descricoes, hovertemplate=HOVER))
        fig.update_layout(
            title=dict(
                text=f"{bloco_nome}<br><sup>Média do bloco: {media_bloco} — {media_label}</sup>" if media_bloco else bloco_nome,
                font=dict(size=15),
            ),
            yaxis=dict(range=[0, 4.5], tickvals=[1, 2, 3, 4]),
            height=320,
            margin=dict(t=60, b=60, l=40, r=20),
            font=dict(family="Inter, sans-serif"),
        )
        figs.append(fig)
    return figs


def linha_historico(historico: list) -> go.Figure:
    if not historico:
        return None
    df = pd.DataFrame(historico)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["periodo"], y=df["total_colaborador"],
        name="Autoavaliação", line=dict(color=COR_COLABORADOR, width=2), mode="lines+markers",
    ))
    fig.add_trace(go.Scatter(
        x=df["periodo"], y=df["total_gestor"],
        name="Gestor", line=dict(color=COR_GESTOR, width=2), mode="lines+markers",
    ))
    fig.update_layout(
        title="Evolução ao longo do tempo",
        yaxis=dict(title="Pontuação total"),
        xaxis=dict(title="Período"),
        legend=dict(orientation="h", y=-0.25),
        height=350,
        margin=dict(t=40, b=60),
        font=dict(family="Inter, sans-serif"),
    )
    return fig
