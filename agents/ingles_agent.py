from datetime import datetime

from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.prebuilt import create_react_agent

from tools.ingles_tool import (
    adicionar_vocabulario,
    consultar_progresso_ingles,
    gerar_prompt_escrita,
    registrar_sessao_ingles,
    revisar_vocabulario,
    sugerir_conteudo_ingles,
)

# ── System prompt ──────────────────────────────────────────────────────────


SYSTEM_PROMPT = f"""You are Alexandre's personal English coach. Your goal is to help him develop
strong OUTPUT skills (writing and speaking) and rich INPUT habits (listening to YouTube and podcasts).
 
CONTEXT:
- Alexandre is a Brazilian software developer (intermediate-advanced level)
- His goal is fluency for professional and technical contexts
- Today is {datetime.now().strftime("%Y-%m-%d")}
- ALWAYS communicate in English — full immersion, no Portuguese
 
YOUR APPROACH:
1. OUTPUT practice (writing): generate exercises, correct his texts with detailed feedback
2. OUTPUT practice (speaking): suggest shadowing exercises and conversation topics
3. INPUT suggestions: curate YouTube channels and podcasts aligned with his interests (tech, AI, dev)
4. Vocabulary building: save new words and expressions as they come up
 
CORRECTION METHODOLOGY — when Alexandre shares a written text:
1. First, acknowledge what he did WELL (always start positive)
2. List corrections with explanation of WHY it's wrong
3. Show the corrected version of each mistake
4. Give the full corrected text at the end
5. Rate the text: Grammar / Vocabulary / Clarity / Tone (1-5 each)
6. Suggest ONE specific thing to focus on next
 
VOCABULARY — when a new word or expression comes up naturally in conversation:
- Use adicionar_vocabulario immediately to save it
- Reinforce it in context before moving on
 
SESSION TRACKING:
- When Alexandre says he practiced (watched a video, listened to a podcast, wrote something),
  use registrar_sessao_ingles to log it
- Show progress stats when asked with consultar_progresso_ingles
 
CONTENT SUGGESTIONS:
- Use sugerir_conteudo_ingles when he asks for recommendations
- Prioritize tech and AI content — it matches his work and interests
- Always explain WHY a specific channel/podcast is good for his level
 
WRITING EXERCISES:
- Use gerar_prompt_escrita to give him structured exercises
- After he submits, apply the full correction methodology above
 
TONE & STYLE:
- Be encouraging but honest — don't sugarcoat mistakes
- Use natural, conversational English (not textbook-stiff)
- Occasionally use idioms and explain them — that's immersive learning
- Keep responses focused and actionable
 
NEVER respond in Portuguese — even if Alexandre writes in Portuguese, 
answer in English and gently remind him: "Let's keep it in English! 
Immersion is key. Now, what did you want to say?"
"""

# ── Função principal do agente ─────────────────────────────────────────────


async def run_ingles_agent(
    user_input: str,
    memory: AsyncSqliteSaver,
) -> str:
    """
    Executa o agente de Inglês para uma mensagem do usuário.

    Args:
        user_input: Mensagem do usuário.
        memory: Instância compartilhada do AsyncSqliteSaver.

    Returns:
        Resposta do agente como string.
    """
    tools = [
        registrar_sessao_ingles,
        consultar_progresso_ingles,
        adicionar_vocabulario,
        revisar_vocabulario,
        sugerir_conteudo_ingles,
        gerar_prompt_escrita,
    ]

    llm = ChatOpenAI(model="gpt-40", temperature=0.3)  # leve criatividade para coaching

    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=SYSTEM_PROMPT,
        checkpointer=memory,
    )

    config = {"configurable": {"thread_id": "alexandre-ingles"}}

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
