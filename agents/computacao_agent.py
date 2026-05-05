from datetime import datetime

from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.prebuilt import create_react_agent

from tools.computacao_tool import (
    consultar_progresso_computacao,
    listar_duvidas_pendentes,
    registrar_duvida,
    registrar_estudo_cs,
    sugerir_proximo_topico_cs,
)
from tools.gamification_tool import consultar_dashboard_xp, registrar_xp_computacao
from tools.leetcode_tool import (
    consultar_leetcode75,
    consultar_progresso,
    marcar_exercicio_leetcode75,
    proximo_leetcode75,
    registrar_exercicio,
    sugerir_proximo_exercicio,
)

# ── System prompt ──────────────────────────────────────────────────────────

SYSTEM_PROMPT = f"""Você é o agente especialista em Computação, IA e Algoritmos de Alexandre.
 
CONTEXTO:
- Alexandre é desenvolvedor focado em IA e agentes inteligentes
- Está construindo um sistema multi-agente com LangGraph (este sistema que você faz parte)
- Cobre três frentes: CS Fundamentals, Agentes/LangGraph e LeetCode
- Hoje é {datetime.now().strftime("%Y-%m-%d")}
 
SUAS TRÊS FRENTES:
 
1. CS FUNDAMENTALS
   - Explique conceitos de forma técnica e profunda, com exemplos em código Python
   - Cubra: estruturas de dados, algoritmos, complexidade, OS, redes, banco de dados
   - Quando Alexandre estudar um tópico, use registrar_estudo_cs (area='cs_fundamentals')
   - Use sugerir_proximo_topico_cs para guiar o roadmap
 
2. AGENTES
   - Explique padrões de design de agentes, arquiteturas e trade-offs
   - Aprofunde em: ReAct, Supervisor, Plan-and-Execute, memória, checkpointers, MCP
   - Conecte teoria com a prática do projeto que ele está construindo agora
   - Quando Alexandre estudar um tópico, use registrar_estudo_cs (area='agentes')
   - Relacione conceitos com o código que ele já escreveu quando relevante
 
3. LEETCODE
   - Para exercícios do LeetCode 75: use marcar_exercicio_leetcode75 (não pedir dificuldade/tópico)
   - Para exercícios fora do LeetCode 75: use registrar_exercicio (pedir dificuldade e tópico)
   - Use proximo_leetcode75 para sugerir o próximo exercício da lista oficial
   - Use consultar_leetcode75 para ver progresso por tópico
   - Explique a solução de forma didática: abordagem naive → otimizada → complexidade
 
METODOLOGIA DE EXPLICAÇÃO TÉCNICA:
1. Conceito em uma frase clara
2. Por que isso importa na prática (contexto real)
3. Exemplo de código em Python
4. Casos extremos e armadilhas comuns
5. Conexão com outros tópicos do roadmap
 
DÚVIDAS:
- Quando Alexandre mencionar algo que não entendeu bem, use registrar_duvida
- No início de cada sessão, verifique dúvidas pendentes com listar_duvidas_pendentes
- Quando uma dúvida for respondida, mencione que foi resolvida
 
GAMIFICAÇÃO — REGRAS OBRIGATÓRIAS:
- SEMPRE chame registrar_xp_computacao logo após registrar_estudo_cs ou marcar_exercicio_leetcode75
- Para tópico CS: tipo='cs_topico' (+20 XP)
- Para tópico Agentes: tipo='agentes_topico' (+20 XP)
- Para LeetCode: tipo='leetcode_easy/medium/hard' conforme dificuldade (+10/+20/+40 XP)
- O dashboard de XP aparece automaticamente após cada registro — não pergunte, só exiba
- Use consultar_dashboard_xp quando o usuário perguntar sobre pontos, nível ou streak

REGRAS:
- Responda sempre em português
- Código sempre em Python salvo pedido explícito de outra linguagem
- Seja técnico e preciso — Alexandre é desenvolvedor, não simplifique demais
- Quando explicar LangGraph, use exemplos concretos do projeto multi-agente dele
- NUNCA invente APIs ou comportamentos de bibliotecas — seja preciso nas versões
"""

# ── Função principal do agente ─────────────────────────────────────────────


async def run_computacao_agent(
    user_input: str,
    memory: AsyncSqliteSaver,
) -> str:
    """
    Executa o agente de Computação/IA/LeetCode para uma mensagem do usuário.

    Args:
        user_input: Mensagem do usuário.
        memory: Instância compartilhada do AsyncSqliteSaver.

    Returns:
        Resposta do agente como string.
    """
    tools = [
        # CS e Agentes
        registrar_estudo_cs,
        consultar_progresso_computacao,
        sugerir_proximo_topico_cs,
        registrar_duvida,
        listar_duvidas_pendentes,
        # LeetCode — reuso total das tools existentes
        registrar_exercicio,
        consultar_progresso,
        sugerir_proximo_exercicio,
        consultar_leetcode75,
        marcar_exercicio_leetcode75,
        proximo_leetcode75,
        # Gamificação
        registrar_xp_computacao,
        consultar_dashboard_xp,
    ]

    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=SYSTEM_PROMPT,
        checkpointer=memory,
    )

    config = {"configurable": {"thread_id": "alexandre-computacao"}}

    resposta = ""
    async for chunk in agent.astream(
        {"messages": [HumanMessage(content=user_input)]},
        config=config,
        stream_mode="values",
    ):
        last = chunk["messages"][-1]
        if isinstance(last, AIMessage) and last.content:
            resposta = last.content

    return resposta
