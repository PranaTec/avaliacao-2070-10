import os
import secrets
from typing import Optional
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

_client = None

def get_client():
    global _client
    if _client is None:
        url = os.environ["SUPABASE_URL"]
        key = os.environ["SUPABASE_KEY"]
        _client = create_client(url, key)
    return _client


BLOCOS_PADRAO = [
    {
        "nome": "DESEMPENHO",
        "ordem": 1,
        "criterios": [
            ("PRODUTIVIDADE", "Quantidade e qualidade do trabalho apresentado"),
            ("DISPOSIÇÃO", "Disponibilidade para colaboração com o trabalho da equipe"),
            ("INICIATIVA", "Colaboração espontânea para tomar providências e solucionar problemas"),
            ("AUTONOMIA", "Atitudes de resolução diante das dificuldades de execução de procedimentos"),
            ("LIDERANÇA", "Modo como influencia os colegas na direção dos objetivos e metas de trabalho"),
            ("METAS", "Alcance de objetivos e metas de trabalho com eficácia"),
        ],
    },
    {
        "nome": "COMPORTAMENTO EMPRESARIAL",
        "ordem": 2,
        "criterios": [
            ("RESPONSABILIDADE", "Atitudes de obediência às normas e procedimentos determinados pela empresa"),
            ("ÉTICA", "Atitudes de idoneidade, cidadania e integridade com relação à empresa, aos clientes e à comunidade"),
            ("ASSIDUIDADE", "Ausência de faltas e atrasos"),
            ("INTERAÇÃO", "Comunicação positiva e bom relacionamento com superiores, colegas e clientes"),
            ("GESTÃO DE CONFLITOS", "Solução de problemas e dificuldades dos funcionários entre si e com relação aos procedimentos"),
            ("GESTÃO DE RECURSOS", "Utiliza os recursos da empresa com eficiência e cuidado, evitando desperdícios"),
        ],
    },
    {
        "nome": "NEGÓCIO",
        "ordem": 3,
        "criterios": [
            ("NEGÓCIO", "Demonstração de atitudes relacionadas com os serviços da empresa e interesse do cliente"),
            ("PRODUTO", "Domínio dos produtos e serviços da empresa"),
            ("MVV", "Aplicação dos valores da empresa"),
            ("RESULTADO", "Geração de resultados com seu trabalho"),
        ],
    },
]


# ── Empresas ──────────────────────────────────────────────────────────────────

def criar_empresa(nome: str) -> dict:
    db = get_client()
    token = secrets.token_urlsafe(16)
    res = db.table("empresas").insert({"nome": nome, "token_gestor": token}).execute()
    empresa = res.data[0]
    _seed_blocos_e_criterios(empresa["id"])
    return empresa


def buscar_empresa_por_token(token: str) -> Optional[dict]:
    db = get_client()
    res = db.table("empresas").select("*").eq("token_gestor", token).execute()
    return res.data[0] if res.data else None


def listar_empresas() -> list:
    db = get_client()
    return db.table("empresas").select("*").order("nome").execute().data


def _seed_blocos_e_criterios(empresa_id: str):
    db = get_client()
    for bloco_def in BLOCOS_PADRAO:
        bloco_res = db.table("blocos").insert({
            "nome": bloco_def["nome"],
            "ordem": bloco_def["ordem"],
            "empresa_id": empresa_id,
        }).execute()
        bloco_id = bloco_res.data[0]["id"]
        for i, (nome, descricao) in enumerate(bloco_def["criterios"], start=1):
            db.table("criterios").insert({
                "nome": nome,
                "descricao": descricao,
                "bloco_id": bloco_id,
                "empresa_id": empresa_id,
                "ordem": i,
            }).execute()


# ── Colaboradores ─────────────────────────────────────────────────────────────

def criar_colaborador(empresa_id: str, nome: str, funcao: str, data_admissao: Optional[str] = None) -> dict:
    db = get_client()
    payload = {"nome": nome, "funcao": funcao, "empresa_id": empresa_id}
    if data_admissao:
        payload["data_admissao"] = data_admissao
    return db.table("colaboradores").insert(payload).execute().data[0]


def buscar_colaborador_por_id(colaborador_id: str) -> Optional[dict]:
    res = get_client().table("colaboradores").select("*").eq("id", colaborador_id).execute()
    return res.data[0] if res.data else None


def atualizar_colaborador(colaborador_id: str, nome: str, funcao: str, data_admissao: Optional[str] = None):
    payload = {"nome": nome, "funcao": funcao}
    if data_admissao:
        payload["data_admissao"] = data_admissao
    get_client().table("colaboradores").update(payload).eq("id", colaborador_id).execute()


def desativar_colaborador(colaborador_id: str):
    get_client().table("colaboradores").update({"ativo": False}).eq("id", colaborador_id).execute()


def listar_colaboradores(empresa_id: str) -> list:
    db = get_client()
    return (
        db.table("colaboradores")
        .select("*")
        .eq("empresa_id", empresa_id)
        .eq("ativo", True)
        .order("nome")
        .execute()
        .data
    )


# ── Blocos e Critérios ────────────────────────────────────────────────────────

def listar_blocos_com_criterios(empresa_id: str) -> list:
    db = get_client()
    blocos = (
        db.table("blocos")
        .select("*")
        .eq("empresa_id", empresa_id)
        .order("ordem")
        .execute()
        .data
    )
    for bloco in blocos:
        criterios = (
            db.table("criterios")
            .select("*")
            .eq("bloco_id", bloco["id"])
            .eq("ativo", True)
            .order("ordem")
            .execute()
            .data
        )
        bloco["criterios"] = criterios
    return blocos


def atualizar_criterio(criterio_id: str, nome: str, descricao: str):
    get_client().table("criterios").update({"nome": nome, "descricao": descricao}).eq("id", criterio_id).execute()


def adicionar_criterio(bloco_id: str, empresa_id: str, nome: str, descricao: str, ordem: int):
    get_client().table("criterios").insert({
        "nome": nome, "descricao": descricao,
        "bloco_id": bloco_id, "empresa_id": empresa_id, "ordem": ordem
    }).execute()


def remover_criterio(criterio_id: str):
    get_client().table("criterios").update({"ativo": False}).eq("id", criterio_id).execute()


# ── Avaliações ────────────────────────────────────────────────────────────────

def buscar_avaliacao_existente(colaborador_id: str, empresa_id: str, periodo: str) -> Optional[dict]:
    res = (get_client().table("avaliacoes")
           .select("*")
           .eq("colaborador_id", colaborador_id)
           .eq("empresa_id", empresa_id)
           .eq("periodo", periodo)
           .execute())
    return res.data[0] if res.data else None


def criar_avaliacao(colaborador_id: str, empresa_id: str, periodo: str) -> dict:
    db = get_client()
    avaliacao = db.table("avaliacoes").insert({
        "colaborador_id": colaborador_id,
        "empresa_id": empresa_id,
        "periodo": periodo,
        "token_colaborador": secrets.token_urlsafe(20),
        "token_gestor": secrets.token_urlsafe(20),
    }).execute().data[0]

    criterios = db.table("criterios").select("id").eq("empresa_id", empresa_id).eq("ativo", True).execute().data
    respostas = [{"avaliacao_id": avaliacao["id"], "criterio_id": c["id"]} for c in criterios]
    if respostas:
        db.table("respostas").insert(respostas).execute()

    return avaliacao


def buscar_avaliacao_por_token(token: str, tipo: str) -> Optional[dict]:
    db = get_client()
    campo = "token_colaborador" if tipo == "colaborador" else "token_gestor"
    res = db.table("avaliacoes").select("*, colaboradores(nome, funcao), empresas(nome)").eq(campo, token).execute()
    return res.data[0] if res.data else None


def listar_avaliacoes_empresa(empresa_id: str) -> list:
    db = get_client()
    return (
        db.table("avaliacoes")
        .select("*, colaboradores(nome, funcao)")
        .eq("empresa_id", empresa_id)
        .order("criado_em", desc=True)
        .execute()
        .data
    )


def buscar_avaliacao_por_id(avaliacao_id: str) -> Optional[dict]:
    db = get_client()
    res = db.table("avaliacoes").select("*, colaboradores(nome, funcao), empresas(nome)").eq("id", avaliacao_id).execute()
    return res.data[0] if res.data else None


# ── Respostas ─────────────────────────────────────────────────────────────────

def buscar_respostas(avaliacao_id: str) -> list:
    db = get_client()
    return (
        db.table("respostas")
        .select("*, criterios(nome, descricao, ordem, bloco_id, blocos(nome, ordem))")
        .eq("avaliacao_id", avaliacao_id)
        .execute()
        .data
    )


def salvar_respostas_colaborador(avaliacao_id: str, respostas: dict):
    from datetime import datetime, timezone
    db = get_client()
    agora = datetime.now(timezone.utc).isoformat()
    for criterio_id, nota in respostas.items():
        db.table("respostas").update({
            "nota_colaborador": nota,
            "preenchido_colaborador_em": agora,
        }).eq("avaliacao_id", avaliacao_id).eq("criterio_id", criterio_id).execute()
    _atualizar_status(avaliacao_id, "colaborador")


def salvar_respostas_gestor(avaliacao_id: str, respostas: dict):
    from datetime import datetime, timezone
    db = get_client()
    agora = datetime.now(timezone.utc).isoformat()
    for criterio_id, nota in respostas.items():
        db.table("respostas").update({
            "nota_gestor": nota,
            "preenchido_gestor_em": agora,
        }).eq("avaliacao_id", avaliacao_id).eq("criterio_id", criterio_id).execute()
    _atualizar_status(avaliacao_id, "gestor")


def _atualizar_status(avaliacao_id: str, quem: str):
    db = get_client()
    av = db.table("avaliacoes").select("status").eq("id", avaliacao_id).execute().data[0]
    status_atual = av["status"]
    if quem == "colaborador":
        novo = "completa" if status_atual == "gestor_ok" else "colaborador_ok"
    else:
        novo = "completa" if status_atual == "colaborador_ok" else "gestor_ok"
    db.table("avaliacoes").update({"status": novo}).eq("id", avaliacao_id).execute()


# ── Observações ──────────────────────────────────────────────────────────────

def salvar_observacoes(avaliacao_id: str, texto: str):
    get_client().table("avaliacoes").update({"observacoes": texto}).eq("id", avaliacao_id).execute()


# ── Histórico ────────────────────────────────────────────────────────────────

def historico_colaborador(colaborador_id: str) -> list:
    db = get_client()
    avaliacoes = (
        db.table("avaliacoes")
        .select("id, periodo, status")
        .eq("colaborador_id", colaborador_id)
        .eq("status", "completa")
        .order("periodo")
        .execute()
        .data
    )
    historico = []
    for av in avaliacoes:
        respostas = db.table("respostas").select("nota_colaborador, nota_gestor").eq("avaliacao_id", av["id"]).execute().data
        total_c = sum(r["nota_colaborador"] for r in respostas if r["nota_colaborador"])
        total_g = sum(r["nota_gestor"] for r in respostas if r["nota_gestor"])
        historico.append({"periodo": av["periodo"], "total_colaborador": total_c, "total_gestor": total_g})
    return historico
