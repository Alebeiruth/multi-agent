import os
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.tools.retriever import create_retriever_tool
from langchain_mcp_adapters.client import MultiServerMCPClient

from tools.estatistica_tool import (
    registrar_aula,
    consultar_progresso_estatistica,
    calcular_revisoes,
    marcar_revisao_feita,
    gerar_conteudo_email_revisao,
)
from tools.calendar_tool import agendar_sessao


# ── RAG — PDFs das aulas de estatística ───────────────────────────────────

def build_rag_tool():
    """Constrói o retriever RAG sobre os PDFs das aulas de estatística."""
    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-large-en-v1.5",
        model_kwargs={"device": "cpu"},
    )
    vectorstore = Chroma(
        persist_directory="./chroma_db_estatistica",
        embedding_function=embeddings,
        collection_name="estatistica",
    )
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 4},
    )
    return create_retriever_tool(
        retriever=retriever,
        name="buscar_conteudo_aula",
        description=(
            "Busca conteúdo nos PDFs e slides das aulas de Estatística e Probabilidade. "
            "Use quando o usuário perguntar sobre fórmulas, conceitos, definições ou "
            "exemplos de qualquer tópico da matéria."
        ),
    )


# ── System prompt ──────────────────────────────────────────────────────────

SYSTEM_PROMPT = f"""Você é o agente especialista em Estatística e Probabilidade de Alexandre.

CONTEXTO:
- A matéria tem 8 aulas no total, todas às quartas-feiras
- As revisões seguem o padrão: quinta (D+1), sábado (D+3), terça (D+5)
- Hoje é {datetime.now().strftime('%Y-%m-%d (%A)')}
- Ao registrar uma aula, SEMPRE agende as revisões no Calendar e envie os emails

FLUXO AO REGISTRAR UMA AULA NOVA:
1. Chame registrar_aula para salvar no storage
2. Chame calcular_revisoes para obter as datas
3. Para cada revisão (1, 2 e 3), chame agendar_sessao para criar o evento no Calendar
4. Para cada revisão, chame gerar_conteudo_email_revisao e depois use o Gmail MCP
   para enviar o email com o assunto e corpo retornados

PARÂMETROS para agendar_sessao de revisão:
- tipo: 'estatistica'
- titulo: '📐 Revisão [N]: [tema da aula]'
- descricao: conteúdos da aula + observações
- data_inicio: data retornada por calcular_revisoes (formato 'YYYY-MM-DD HH:MM')
- duracao_minutos: 45

PARÂMETROS para o Gmail MCP:
- Use a tool 'send_email' do Gmail MCP
- Preencha 'to', 'subject' e 'body' com os valores de gerar_conteudo_email_revisao
- Envie um email por revisão (3 emails no total)

CAPACIDADES:
- Responder dúvidas sobre qualquer tópico da matéria usando buscar_conteudo_aula
- Registrar aulas assistidas e calcular automaticamente as datas de revisão
- Agendar lembretes no Google Calendar
- Enviar emails de revisão via Gmail
- Mostrar progresso geral da matéria
- Marcar revisões como concluídas

REGRAS:
- Responda sempre em português
- Seja direto e técnico — Alexandre é estudante de computação
- NUNCA invente fórmulas ou definições — use sempre buscar_conteudo_aula
- Se o PDF da aula não estiver indexado, avise o usuário para rodar o ingest
- Quando o usuário disser que fez uma revisão, use marcar_revisao_feita imediatamente
"""


# ── Função principal do agente ─────────────────────────────────────────────

async def run_estatistica_agent(
    user_input: str,
    memory: AsyncSqliteSaver,
    mcp_client: MultiServerMCPClient,
) -> str:
    """
    Executa o agente de Estatística para uma mensagem do usuário.

    Args:
        user_input: Mensagem do usuário.
        memory: Instância compartilhada do AsyncSqliteSaver.
        mcp_client: Cliente MCP já inicializado com Calendar e Gmail.

    Returns:
        Resposta do agente como string.
    """
    # tools MCP filtradas para este agente
    mcp_tools = await mcp_client.get_tools()
    tools_mcp_permitidas = [
        "create_event", "list_events",          # Google Calendar
        "send_email", "search_emails",           # Gmail
    ]
    mcp_tools_filtradas = [t for t in mcp_tools if t.name in tools_mcp_permitidas]

    # tools Python do agente
    python_tools = [
        build_rag_tool(),
        registrar_aula,
        consultar_progresso_estatistica,
        calcular_revisoes,
        marcar_revisao_feita,
        gerar_conteudo_email_revisao,
        agendar_sessao,
    ]

    all_tools = python_tools + mcp_tools_filtradas

    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    agent = create_react_agent(
        model=llm,
        tools=all_tools,
        prompt=SYSTEM_PROMPT,
        checkpointer=memory,
    )

    config = {"configurable": {"thread_id": "alexandre-estatistica"}}

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