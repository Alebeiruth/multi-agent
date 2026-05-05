from datetime import datetime
import json
import os

from langchain_core.tools import tool
from pydantic import ValidationError

from tools.validators import (
    RegistrarModuloAWSInput,
    RegistrarModuloDCInput,
)

STORAGE_FILE = "storage/aws/aws.json"

# ── Roadmaps dos cursos ────────────────────────────────────────────────────

ROADMAP_AWS_SAA = [
    # Cloud Foundations
    "Cloud Computing — Conceitos e Modelos",
    "IAM — Users, Groups, Roles e Policies",
    "EC2 — Instâncias, Tipos e Pricing",
    "EC2 — Security Groups e Key Pairs",
    "EC2 — EBS, EFS e Instance Store",
    "EC2 — Load Balancers (ALB, NLB, CLB)",
    "EC2 — Auto Scaling Groups",
    # Storage
    "S3 — Buckets, Objects e Versionamento",
    "S3 — Storage Classes e Lifecycle",
    "S3 — Security, Encryption e ACLs",
    "S3 — Replication e Performance",
    "RDS — MySQL, PostgreSQL, Aurora",
    "RDS — Multi-AZ e Read Replicas",
    "ElastiCache — Redis e Memcached",
    "DynamoDB — Conceitos e Operações",
    # Networking
    "VPC — Subnets, Route Tables e IGW",
    "VPC — NAT Gateway e VPC Peering",
    "VPC — Security Groups vs NACLs",
    "Route 53 — DNS e Routing Policies",
    "CloudFront — CDN e Edge Locations",
    # Integration & Messaging
    "SQS — Filas e Dead Letter Queues",
    "SNS — Topics e Subscribers",
    "Lambda — Functions e Event Sources",
    "API Gateway — REST e HTTP APIs",
    # Monitoring & Security
    "CloudWatch — Metrics, Logs e Alarms",
    "CloudTrail — Auditoria e Compliance",
    "KMS — Chaves e Criptografia",
    "WAF e Shield — Proteção DDoS",
    # Architecture
    "Well-Architected Framework — 6 Pilares",
    "High Availability e Fault Tolerance",
    "Disaster Recovery — Estratégias",
    "Cost Optimization — Estratégias",
]

ROADMAP_DATACAMP = {
    "Data Scientist": [
        "Introdução ao Python",
        "Python intermediario",
        "Investigando filmes da Netflix",
        "Manipulação de dados com o pandas",
        "Explorando as notas dos testes das escolas públicas de NYC",
        "Junção de dados com o pandas",
        "Introdução a estatistica em Python",
        "Introdução a Visualização de Dados com a Matplotlib",
        "Introdução a Visualização de Dados com o Seaborn",
        "Visualizando a história dos vencedores do Prêmio Nobel",
        "Introdução a funções em Python",
        "Caixa de ferramentas Python",
        "Manipulação de Dados com Python",
        "Análise Exploratória de Dados em Python",
        "Analisando o Crime em Los Angeles",
        "Trabalhando com dados categóricos em Python",
        "Customer Analytics: Preparing Data for Modeling",
        "Conceitos de comunicação de dados",
        "Introdução a importação de dados em Python",
        "Limpeza de dados em Python",
        "Exploring Airbnb Market Trends",
        "Trabalhando com datas e horários em Python",
        "Importando e Limpando Dados co Python",
        "Como escrever funções em Python",
        "Programação em Python",
        "Introdução a Regressão com stasmodels em Python",
        "Modeling Car Insurance Claim Outcomes",
        "Amostragem em Python",
        "Teste de hipóteses em Python",
        "Projeto experimental em Python",
        "Hypothesis Testing with Men's and Women's Soccer Matches",
        "Aprendizado Supervisionado com o scikit-learn",
        "Modelagem Preditiva para Agricultura",
        "Unsupervised Learning em Python",
        "Clustering Antarctic Penguin Species",
        "Aprendizado de maquina com modelos baseadis em árvores em Python",
        "Predicting Movie Rental Durantiosn",
    ],
}

# ── Helpers ────────────────────────────────────────────────────────────────


def _load() -> dict:
    if not os.path.exists(STORAGE_FILE):
        return {"modulos_aws": [], "modulos_datacamp": [], "duvidas": []}
    with open(STORAGE_FILE, encoding="utf-8") as f:
        content = f.read().strip()
        if not content:
            return {"modulos_aws": [], "modulos_datacamp": [], "duvidas": []}
        return json.loads(content)


def _save(data: dict):
    os.makedirs(os.path.dirname(STORAGE_FILE), exist_ok=True)
    with open(STORAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ── Tool 1: registrar módulo AWS ──────────────────────────────────────────


@tool
def registrar_modulo_aws(
    topico: str,
    duracao_minutos: int,
    status: str = "concluido",
    observacoes: str = "",
) -> str:
    """
    Registra um módulo ou tópico do curso AWS Solutions Architect Associate concluído.
    Use quando o usuário informar que assistiu uma aula ou concluiu um tópico do curso AWS.

    Args:
        topico: Nome do tópico estudado. Exemplo: 'IAM — Users, Groups, Roles e Policies'.
        duracao_minutos: Duração da sessão em minutos.
        status: 'concluido', 'revisando' ou 'com_duvidas'. Padrão: 'concluido'.
        observacoes: Pontos importantes ou dúvidas encontradas.

    Returns:
        Confirmação do registro com progresso atualizado no curso AWS.
    """
    try:
        RegistrarModuloAWSInput(
            topico=topico,
            duracao_minutos=duracao_minutos,
            status=status,
            observacoes=observacoes,
        )
    except ValidationError as e:
        return f"Erro de validação: {e.errors()[0]['msg']}"

    data = _load()

    modulo = {
        "topico": topico,
        "duracao_minutos": duracao_minutos,
        "status": status,
        "observacoes": observacoes,
        "data": datetime.now().strftime("%Y-%m-%d"),
    }

    data["modulos_aws"].append(modulo)
    _save(data)

    topicos_feitos = {m["topico"] for m in data["modulos_aws"]}
    total = len(ROADMAP_AWS_SAA)
    feitos = len([t for t in ROADMAP_AWS_SAA if t in topicos_feitos])
    pct = int(feitos / total * 100)

    return (
        f"✅ '{topico}' registrado no curso AWS SAA.\n"
        f"Progresso AWS SAA: {feitos}/{total} tópicos ({pct}%)"
    )


# ── Tool 2: registrar módulo Datacamp ────────────────────────────────────


@tool
def registrar_modulo_datacamp(
    curso: str,
    modulo: str,
    duracao_minutos: int,
    status: str = "concluido",
    observacoes: str = "",
) -> str:
    """
    Registra um módulo do Datacamp concluído.
    Use quando o usuário informar que concluiu um módulo ou curso no Datacamp.

    Args:
        curso: Nome da trilha ou curso. Exemplo: 'Machine Learning', 'Python', 'AI & LLMs'.
        modulo: Nome do módulo específico. Exemplo: 'Supervised Learning with scikit-learn'.
        duracao_minutos: Duração da sessão em minutos.
        status: 'concluido', 'em_andamento' ou 'revisando'. Padrão: 'concluido'.
        observacoes: Insights ou conceitos importantes aprendidos.

    Returns:
        Confirmação com progresso na trilha do Datacamp.
    """
    try:
        RegistrarModuloDCInput(
            curso=curso,
            modulo=modulo,
            duracao_minutos=duracao_minutos,
            status=status,
            observacoes=observacoes,
        )
    except ValidationError as e:
        return f"Erro de validação: {e.errors()[0]['msg']}"

    data = _load()

    entrada = {
        "curso": curso,
        "modulo": modulo,
        "duracao_minutos": duracao_minutos,
        "status": status,
        "observacoes": observacoes,
        "data": datetime.now().strftime("%Y-%m-%d"),
    }

    data["modulos_datacamp"].append(entrada)
    _save(data)

    # progresso na trilha
    modulos_trilha = ROADMAP_DATACAMP.get(curso, [])
    feitos_trilha = {m["modulo"] for m in data["modulos_datacamp"] if m["curso"] == curso}
    pct = int(len(feitos_trilha) / len(modulos_trilha) * 100) if modulos_trilha else 0

    return (
        f"✅ '{modulo}' registrado — trilha {curso}.\n"
        f"Progresso em {curso}: {len(feitos_trilha)}/{len(modulos_trilha)} módulos ({pct}%)"
    )


# ── Tool 3: consultar progresso geral ─────────────────────────────────────


@tool
def consultar_progresso_aws_datacamp() -> str:
    """
    Retorna o progresso completo nos cursos AWS SAA e Datacamp,
    com breakdown por área e estimativa de tempo restante.
    Use quando o usuário perguntar sobre progresso ou quanto falta para terminar.

    Returns:
        Resumo detalhado do progresso em ambos os cursos.
    """
    data = _load()

    modulos_aws = data.get("modulos_aws", [])
    modulos_dc = data.get("modulos_datacamp", [])

    linhas = ["☁️  Progresso — AWS SAA + Datacamp\n"]

    # AWS SAA
    topicos_feitos_aws = {m["topico"] for m in modulos_aws}
    feitos_aws = len([t for t in ROADMAP_AWS_SAA if t in topicos_feitos_aws])
    total_aws = len(ROADMAP_AWS_SAA)
    pct_aws = int(feitos_aws / total_aws * 100)
    tempo_aws = sum(m["duracao_minutos"] for m in modulos_aws)
    pendentes_aws = [t for t in ROADMAP_AWS_SAA if t not in topicos_feitos_aws]

    linhas.append("🏗️  AWS Solutions Architect Associate")
    linhas.append(f"   Progresso: {feitos_aws}/{total_aws} tópicos ({pct_aws}%)")
    linhas.append(f"   Tempo estudado: {tempo_aws // 60}h {tempo_aws % 60}min")
    if pendentes_aws:
        linhas.append(f"   Próximos: {', '.join(pendentes_aws[:3])}")
    linhas.append("")

    # Datacamp por trilha
    linhas.append("📊 Datacamp")
    total_dc_min = sum(m["duracao_minutos"] for m in modulos_dc)
    linhas.append(f"   Tempo total: {total_dc_min // 60}h {total_dc_min % 60}min\n")

    for trilha, modulos_roadmap in ROADMAP_DATACAMP.items():
        feitos_trilha = {m["modulo"] for m in modulos_dc if m["curso"] == trilha}
        pct = int(len(feitos_trilha) / len(modulos_roadmap) * 100)
        pendentes = [m for m in modulos_roadmap if m not in feitos_trilha]
        linhas.append(f"   {trilha}: {len(feitos_trilha)}/{len(modulos_roadmap)} ({pct}%)")
        if pendentes:
            linhas.append(f"   → Próximo: {pendentes[0]}")

    return "\n".join(linhas)


# ── Tool 4: sugerir próximo tópico ────────────────────────────────────────


@tool
def sugerir_proximo_aws_datacamp(plataforma: str = "") -> str:
    """
    Sugere o próximo tópico a estudar no AWS SAA ou Datacamp seguindo o roadmap.

    Args:
        plataforma: 'aws' ou 'datacamp'. Deixe vazio para sugestão automática
                    baseada em qual está mais atrasado proporcionalmente.

    Returns:
        Próximo tópico sugerido com contexto e dica de estudo.
    """
    data = _load()

    topicos_aws = {m["topico"] for m in data.get("modulos_aws", [])}
    pendentes_aws = [t for t in ROADMAP_AWS_SAA if t not in topicos_aws]
    pct_aws = 1 - (len(pendentes_aws) / len(ROADMAP_AWS_SAA))

    # calcula menor progresso no Datacamp
    pcts_dc = {}
    for trilha, modulos in ROADMAP_DATACAMP.items():
        feitos = {m["modulo"] for m in data.get("modulos_datacamp", []) if m["curso"] == trilha}
        pcts_dc[trilha] = len(feitos) / len(modulos)
    trilha_menor = min(pcts_dc, key=pcts_dc.get)
    pct_dc = pcts_dc[trilha_menor]

    if not plataforma:
        plataforma = "aws" if pct_aws <= pct_dc else "datacamp"

    if plataforma == "aws":
        if not pendentes_aws:
            return "🏆 Você concluiu todos os tópicos do roadmap AWS SAA! Hora de marcar o exame."
        proximo = pendentes_aws[0]
        feitos = len(ROADMAP_AWS_SAA) - len(pendentes_aws)
        return (
            f"📌 Próximo tópico — AWS SAA\n\n"
            f"Tópico: {proximo}\n"
            f"Progresso: {feitos}/{len(ROADMAP_AWS_SAA)}\n\n"
            f"💡 Dica: Após estudar, pratique no AWS Free Tier e faça questões no Udemy."
        )
    else:
        modulos_trilha = ROADMAP_DATACAMP.get(trilha_menor, [])
        feitos_trilha = {
            m["modulo"] for m in data.get("modulos_datacamp", []) if m["curso"] == trilha_menor
        }
        pendentes_dc = [m for m in modulos_trilha if m not in feitos_trilha]
        if not pendentes_dc:
            return f"🏆 Trilha '{trilha_menor}' concluída no Datacamp!"
        proximo = pendentes_dc[0]
        return (
            f"📌 Próximo módulo — Datacamp\n\n"
            f"Trilha: {trilha_menor}\n"
            f"Módulo: {proximo}\n"
            f"Progresso na trilha: {len(feitos_trilha)}/{len(modulos_trilha)}\n\n"
            f"💡 Dica: Complete os exercícios práticos do módulo antes de marcar como concluído."
        )


# ── Tool 5: registrar dúvida de curso ─────────────────────────────────────


@tool
def registrar_duvida_curso(
    plataforma: str,
    topico: str,
    duvida: str,
) -> str:
    """
    Registra uma dúvida técnica de AWS ou Datacamp para revisão futura.
    Use quando o usuário não entender algo ou quiser aprofundar um conceito.

    Args:
        plataforma: 'aws' ou 'datacamp'.
        topico: Tópico relacionado. Exemplo: 'VPC Peering', 'Random Forest'.
        duvida: Descrição da dúvida.

    Returns:
        Confirmação do registro.
    """
    data = _load()

    entrada = {
        "plataforma": plataforma,
        "topico": topico,
        "duvida": duvida,
        "resolvida": False,
        "data": datetime.now().strftime("%Y-%m-%d"),
    }

    data["duvidas"].append(entrada)
    _save(data)

    pendentes = sum(1 for d in data["duvidas"] if not d["resolvida"])
    return (
        f"📝 Dúvida registrada: [{plataforma.upper()}] {topico}\n"
        f"Total de dúvidas pendentes: {pendentes}"
    )


# ── Tool 6: listar dúvidas pendentes ──────────────────────────────────────


@tool
def listar_duvidas_curso() -> str:
    """
    Lista todas as dúvidas pendentes de AWS e Datacamp.
    Use para revisão ou quando o usuário quiser ver o que precisa aprofundar.

    Returns:
        Lista de dúvidas organizadas por plataforma.
    """
    data = _load()
    duvidas = [d for d in data.get("duvidas", []) if not d["resolvida"]]

    if not duvidas:
        return "Nenhuma dúvida pendente. 🎯"

    por_plataforma: dict = {}
    for d in duvidas:
        por_plataforma.setdefault(d["plataforma"], []).append(d)

    linhas = [f"❓ Dúvidas pendentes: {len(duvidas)}\n"]
    for plat, items in por_plataforma.items():
        linhas.append(f"{'☁️  AWS' if plat == 'aws' else '📊 Datacamp'}:")
        for item in items:
            linhas.append(f"  • [{item['topico']}] {item['duvida']} ({item['data']})")

    return "\n".join(linhas)
