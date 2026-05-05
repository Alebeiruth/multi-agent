import asyncio
import os

from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from agents.aws_agent import run_aws_agent
from agents.computacao_agent import run_computacao_agent
from agents.estatistica_agent import run_estatistica_agent
from agents.ingles_agent import run_ingles_agent
from agents.supervisor import Supervisor

load_dotenv()
os.makedirs("storage", exist_ok=True)


# ── LangSmith — tracing ────────────────────────────────────────────────────
# Ativado automaticamente se LANGCHAIN_TRACING_V2=true estiver no .env
# Todas as chamadas de agente, tools e LLM aparecem em smith.langchain.com


def _check_langsmith():
    """Informa se o LangSmith está ativo ao iniciar o sistema."""
    if os.getenv("LANGCHAIN_TRACING_V2", "").lower() == "true":
        project = os.getenv("LANGCHAIN_PROJECT", "multi-agent-coach")
        print(f"  🔍 LangSmith ativo — projeto: {project}")
        print("     Traces em: https://smith.langchain.com")
    else:
        print("  ⚪ LangSmith desativado (LANGCHAIN_TRACING_V2 não definido)")


# ── Configuração MCP ───────────────────────────────────────────────────────

MCP_CONFIG = {
    "google-calendar": {
        "command": r"C:\Program Files\nodejs\npx.cmd",
        "args": ["-y", "mcp-google-calendar"],
        "transport": "stdio",
        "cwd": str(os.path.abspath("./credentials")),
    },
    "gmail": {
        "command": r"C:\Program Files\nodejs\npx.cmd",
        "args": ["-y", "mcp-gmail"],
        "transport": "stdio",
        "cwd": str(os.path.abspath("./credentials")),
    },
}


# ── Dispatcher ─────────────────────────────────────────────────────────────


async def dispatch(
    agent_key: str,
    user_input: str,
    memory: AsyncSqliteSaver,
    mcp_client: MultiServerMCPClient,
) -> str:
    """
    Roteia a mensagem para o agente correto e retorna a resposta.

    Args:
        agent_key: Chave do agente ('estatistica', 'ingles', 'computacao', 'aws').
        user_input: Mensagem do usuário.
        memory: Instância compartilhada do AsyncSqliteSaver.
        mcp_client: Cliente MCP inicializado.

    Returns:
        Resposta do agente como string.
    """
    if agent_key == "estatistica":
        return await run_estatistica_agent(user_input, memory, mcp_client)
    elif agent_key == "ingles":
        return await run_ingles_agent(user_input, memory)
    elif agent_key == "computacao":
        return await run_computacao_agent(user_input, memory)
    elif agent_key == "aws":
        return await run_aws_agent(user_input, memory)
    else:
        return "Nenhum agente ativo. Digite 'menu' para selecionar um agente."


# ── Loop principal ─────────────────────────────────────────────────────────


async def main():
    print("\n" + "═" * 50)
    print("  🎓 Personal Study Coach — Multi-Agent System")
    print("  Carregando... aguarde.")
    _check_langsmith()
    print("═" * 50)

    async with AsyncSqliteSaver.from_conn_string("storage/memory.db") as memory:
        async with MultiServerMCPClient(MCP_CONFIG) as mcp_client:
            supervisor = Supervisor()

            # seleção inicial do agente
            agent_key = supervisor.show_menu()

            if agent_key == "sair":
                print("\nAté logo! 👋\n")
                return

            # mensagem de boas-vindas do agente selecionado
            print(supervisor.greet(agent_key))

            # loop de conversa
            while True:
                try:
                    user_input = input("Você: ").strip()
                except (KeyboardInterrupt, EOFError):
                    print("\n\nAté logo! 👋\n")
                    break

                if not user_input:
                    continue

                # comandos de sistema
                if user_input.lower() in {"sair", "exit", "quit"}:
                    print("\nAté logo! 👋\n")
                    break

                # troca de agente via comando
                if supervisor.handle_switch_command(user_input):
                    agent_key = supervisor.active_agent_key or "supervisor"
                    if agent_key != "supervisor":
                        print(supervisor.greet(agent_key))
                    continue

                # despacha para o agente ativo
                print("\nAgente: ", end="", flush=True)
                try:
                    resposta = await dispatch(agent_key, user_input, memory, mcp_client)
                    print(resposta)
                except Exception as e:
                    print(f"\n[Erro no agente '{agent_key}': {e}]")
                    print("Tente novamente ou digite 'menu' para trocar de agente.")

                print()


if __name__ == "__main__":
    asyncio.run(main())
