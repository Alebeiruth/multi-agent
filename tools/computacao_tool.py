import json
import os
from datetime import datetime
from langchain_core.tools import tool

STORAGE_FILE = "storage/computacao.json"

# Roadmap estruturado por área
ROADMAP = {
    "cs_fundamentals": [
        "Arrays e Strings",
        "Linked Lists",
        "Stacks e Queues",
        "Hash Tables",
        "Trees e BST",
        "Graphs",
        "Heaps",
        "Sorting e Searching",
        "Recursão e Backtracking",
        "Dynamic Programming",
        "Complexidade de Algoritmos (Big-O)",
        "Sistemas Operacionais — Processos e Threads",
        "Sistemas Operacionais — Memória",
        "Redes — TCP/IP e HTTP",
        "Redes — DNS e CDN",
        "Banco de Dados — SQL",
        "Banco de Dados — Índices e Transações",
        "Compiladores — Conceitos básicos",
    ],
    "agentes": [
        "LLMs — Arquitetura Transformer",
        "Prompt Engineering",
        "Function Calling e Tool Use",
        "RAG — Retrieval-Augmented Generation",
        "Embeddings e Vector Stores",
        "LangChain — Chains e Runnables",
        "LangGraph — Grafos de estado",
        "LangGraph — Checkpointer e Memória",
        "Padrões — ReAct Agent",
        "Padrões — Supervisor + Sub-agentes",
        "Padrões — Plan and Execute",
        "MCP — Model Context Protocol",
        "Avaliação de Agentes",
        "Deploy de Agentes",
    ],
}

# ── Helpers ────────────────────────────────────────────────────────────────

def _load() -> dict:
    if not os.path.exists(STORAGE_FILE):
        return {"estudos": [], "duvidas": []}
    with open(STORAGE_FILE, "r", encoding="utf-8") as f:
        content = f.read().strip()
        if not content:
            return {"estudos": [], "duvidas": []}
        return json.loads(content)
 
 
def _save(data: dict):
    os.makedirs("storage", exist_ok=True)
    with open(STORAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
 
# ── Tool 1: registrar sessão de estudo ────────────────────────────────────
 
@tool
def registrar_estudo_cs(
    area: str,
    topico: str,
    duracao_minutos: int,
    status: str = "estudado",
    observacoes: str = "",
) -> str:
    """
    Registra uma sessão de estudo de CS fundamentals ou Agentes.
    Use quando o usuário informar que estudou um tópico específico.
 
    Args:
        area: Área de estudo. Valores: 'cs_fundamentals', 'agentes'.
        topico: Tópico estudado. Exemplo: 'Hash Tables', 'LangGraph — Grafos de estado'.
        duracao_minutos: Duração da sessão em minutos.
        status: 'estudado', 'revisando' ou 'dominado'. Padrão: 'estudado'.
        observacoes: Dúvidas, insights ou recursos utilizados.
 
    Returns:
        Confirmação do registro com progresso atualizado da área.
    """
    data = _load()
 
    estudo = {
        "area": area,
        "topico": topico,
        "duracao_minutos": duracao_minutos,
        "status": status,
        "observacoes": observacoes,
        "data": datetime.now().strftime("%Y-%m-%d"),
    }
 
    data["estudos"].append(estudo)
    _save(data)
 
    # calcula progresso da área
    topicos_area = ROADMAP.get(area, [])
    topicos_estudados = {e["topico"] for e in data["estudos"] if e["area"] == area}
    pct = int(len(topicos_estudados) / len(topicos_area) * 100) if topicos_area else 0
 
    return (
        f"✅ '{topico}' registrado em {area}.\n"
        f"Progresso em {area}: {len(topicos_estudados)}/{len(topicos_area)} tópicos ({pct}%)"
    )
 
 
# ── Tool 2: consultar progresso geral ─────────────────────────────────────
 
@tool
def consultar_progresso_computacao() -> str:
    """
    Retorna o progresso completo de estudos de CS e Agentes,
    com breakdown por área e tópicos pendentes.
    Use quando o usuário perguntar sobre progresso ou o que já estudou.
 
    Returns:
        Resumo completo com progresso por área.
    """
    data = _load()
    estudos = data.get("estudos", [])
 
    if not estudos:
        return "Nenhum estudo registrado ainda. Comece registrando um tópico com registrar_estudo_cs."
 
    total_min = sum(e["duracao_minutos"] for e in estudos)
    total_h = total_min // 60
    total_m = total_min % 60
 
    linhas = [f"💻 Progresso — Computação & Agentes\n"]
    linhas.append(f"Tempo total: {total_h}h {total_m}min — {len(estudos)} sessões\n")
 
    for area, topicos_roadmap in ROADMAP.items():
        topicos_estudados = {e["topico"] for e in estudos if e["area"] == area}
        pendentes = [t for t in topicos_roadmap if t not in topicos_estudados]
        pct = int(len(topicos_estudados) / len(topicos_roadmap) * 100)
 
        label = "CS Fundamentals" if area == "cs_fundamentals" else "Agentes"
        linhas.append(f"📚 {label}: {len(topicos_estudados)}/{len(topicos_roadmap)} ({pct}%)")
 
        if topicos_estudados:
            for t in topicos_roadmap:
                if t in topicos_estudados:
                    st = next(
                        (e["status"] for e in reversed(estudos) if e["topico"] == t), "estudado"
                    )
                    emoji = "🟢" if st == "dominado" else "🟡" if st == "revisando" else "✅"
                    linhas.append(f"  {emoji} {t}")
 
        if pendentes:
            linhas.append(f"  ⬜ Próximos: {', '.join(pendentes[:3])}{'...' if len(pendentes) > 3 else ''}")
 
        linhas.append("")
 
    return "\n".join(linhas)
 
 
# ── Tool 3: sugerir próximo tópico ────────────────────────────────────────
 
@tool
def sugerir_proximo_topico_cs(area: str = "") -> str:
    """
    Sugere o próximo tópico a estudar com base no progresso atual.
    Segue a ordem do roadmap definido.
 
    Args:
        area: Área preferida. Valores: 'cs_fundamentals', 'agentes'.
              Deixe vazio para sugestão automática da área com menos progresso.
 
    Returns:
        Próximo tópico sugerido com contexto e recursos recomendados.
    """
    data = _load()
    estudos = data.get("estudos", [])
    topicos_estudados_por_area = {}
 
    for area_key in ROADMAP:
        topicos_estudados_por_area[area_key] = {
            e["topico"] for e in estudos if e["area"] == area_key
        }
 
    # se área não especificada, escolhe a com menor progresso percentual
    if not area or area not in ROADMAP:
        area = min(
            ROADMAP.keys(),
            key=lambda a: len(topicos_estudados_por_area[a]) / len(ROADMAP[a]),
        )
 
    topicos_feitos = topicos_estudados_por_area[area]
    pendentes = [t for t in ROADMAP[area] if t not in topicos_feitos]
 
    if not pendentes:
        return f"🏆 Você completou todos os tópicos de {area}! Considere revisar os marcados como 'estudado'."
 
    proximo = pendentes[0]
    label = "CS Fundamentals" if area == "cs_fundamentals" else "Agentes"
    feitos = len(topicos_feitos)
    total = len(ROADMAP[area])
 
    recursos = {
        "Arrays e Strings": "NeetCode 150, LeetCode Array/String section",
        "Hash Tables": "NeetCode — Hash Map videos, LeetCode Hash Map problems",
        "LangGraph — Grafos de estado": "LangGraph docs — Quickstart, curso oficial LangChain Academy",
        "RAG — Retrieval-Augmented Generation": "LangChain docs — RAG tutorial, vídeo 'RAG from scratch' Greg Kamradt",
        "Padrões — ReAct Agent": "Paper original ReAct (Yao et al. 2022), LangGraph ReAct tutorial",
        "Padrões — Supervisor + Sub-agentes": "LangGraph multi-agent docs, curso LangChain Academy módulo 4",
    }
 
    recurso_sugerido = recursos.get(proximo, "Documentação oficial + exercícios práticos")
 
    return (
        f"📌 Próximo tópico sugerido — {label}\n\n"
        f"Tópico: {proximo}\n"
        f"Progresso atual: {feitos}/{total}\n\n"
        f"Recursos recomendados:\n  → {recurso_sugerido}"
    )
 
 
# ── Tool 4: registrar dúvida técnica ──────────────────────────────────────
 
@tool
def registrar_duvida(
    topico: str,
    duvida: str,
    area: str = "cs_fundamentals",
) -> str:
    """
    Registra uma dúvida técnica para revisão futura.
    Use quando o usuário mencionar algo que não entendeu bem
    ou quiser marcar um conceito para aprofundar depois.
 
    Args:
        topico: Tópico relacionado à dúvida.
        duvida: Descrição da dúvida ou conceito a aprofundar.
        area: Área. Valores: 'cs_fundamentals', 'agentes'.
 
    Returns:
        Confirmação do registro.
    """
    data = _load()
 
    entrada = {
        "area": area,
        "topico": topico,
        "duvida": duvida,
        "resolvida": False,
        "data": datetime.now().strftime("%Y-%m-%d"),
    }
 
    data["duvidas"].append(entrada)
    _save(data)
 
    pendentes = sum(1 for d in data["duvidas"] if not d["resolvida"])
    return (
        f"📝 Dúvida registrada: '{topico}'\n"
        f"Dúvidas pendentes: {pendentes}"
    )
 
 
# ── Tool 5: listar dúvidas pendentes ──────────────────────────────────────
 
@tool
def listar_duvidas_pendentes() -> str:
    """
    Lista todas as dúvidas técnicas ainda não resolvidas.
    Use quando o usuário quiser ver o que precisa revisar ou aprofundar.
 
    Returns:
        Lista de dúvidas pendentes organizadas por área.
    """
    data = _load()
    duvidas = [d for d in data.get("duvidas", []) if not d["resolvida"]]
 
    if not duvidas:
        return "Nenhuma dúvida pendente. Bom trabalho! 🎯"
 
    por_area: dict = {}
    for d in duvidas:
        por_area.setdefault(d["area"], []).append(d)
 
    linhas = [f"❓ Dúvidas pendentes: {len(duvidas)}\n"]
    for area, items in por_area.items():
        label = "CS Fundamentals" if area == "cs_fundamentals" else "Agentes"
        linhas.append(f"📚 {label}:")
        for item in items:
            linhas.append(f"  • [{item['topico']}] {item['duvida']} ({item['data']})")
 
    return "\n".join(linhas)
