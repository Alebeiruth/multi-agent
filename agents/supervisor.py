import os
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# ── Mapa de agentes disponíveis ────────────────────────────────────────────

AGENTS = {
    "1": {
        "key": "estatistica",
        "label": "📐 Estatística e Probabilidade",
        "description": "Dúvidas das aulas, revisão de conteúdo, agendamento de revisões",
    },
    "2": {
        "key": "ingles",
        "label": "🇺🇸 Inglês",
        "description": "Exercícios de escrita, correção, sugestão de conteúdos",
    },
    "3": {
        "key": "computacao",
        "label": "💻 Computação / IA / LeetCode",
        "description": "CS, IA avançada, agentes, prática de algoritmos",
    },
    "4": {
        "key": "aws",
        "label": "☁️  AWS / Datacamp",
        "description": "Tracking de cursos, dúvidas, agendamento de sessões",
    },
}

# ── System prompt do supervisor ────────────────────────────────────────────

SUPERVISOR_PROMPT = f"""Você é o Supervisor do sistema de estudos pessoal de Alexandre.
 
Sua única responsabilidade é:
1. Receber a mensagem do usuário
2. Identificar qual dos 4 agentes deve responder
3. Retornar APENAS o identificador do agente no formato: ROUTE:<key>
 
Agentes disponíveis:
- estatistica → dúvidas de probabilidade, estatística, aulas da faculdade, revisão, fórmulas
- ingles → prática de inglês, exercícios de escrita, correção de texto, podcasts, YouTube
- computacao → programação, algoritmos, estruturas de dados, LeetCode, IA, agentes, machine learning
- aws → AWS, cloud, Datacamp, cursos, certificações, tracking de módulos
 
Regras:
- Responda SOMENTE com ROUTE:<key> — sem explicações, sem texto adicional
- Em caso de ambiguidade, prefira o agente mais específico
- Se a mensagem for saudação genérica ("oi", "olá"), retorne ROUTE:supervisor
- Hoje é {datetime.now().strftime('%Y-%m-%d')}
 
Exemplos:
"me explica variância" → ROUTE:estatistica
"corrija meu texto em inglês" → ROUTE:ingles
"qual o próximo LeetCode?" → ROUTE:computacao
"quantos módulos fiz no Datacamp?" → ROUTE:aws
"oi, tudo bem?" → ROUTE:supervisor
"""

# ── Classe Supervisor ──────────────────────────────────────────────────────

class Supervisor:
     """
    Responsável por:
    - Exibir menu de seleção de agente
    - Rotear mensagens para o agente correto via LLM
    - Manter referência ao agente ativo na sessão
    """
     
     def __init__(self):
          self.llm = ChatOpenAI(model="gpt-4o", temperature=0)
          self.active_agent_key: str | None = None
        
    
     def show_menu(self) -> str:
         """Exibe o menu de seleção e retorna a key do agente escolhido."""
         print("\n" + "═" * 50)
         print("  🎓 Personal Study Coach — Selecione o agente")
         print("═" * 50)
         for num, agent in AGENTS.items():
              print(f"  {num}. {agent['label']}")
              print(f"     {agent['description']}")
              print("  0. Sair")
              print("═" * 50)
        
         while True:
              choice = input("\nEscolha (0-4): ").strip()
              if choice == "0":
                return "sair"
              if choice in AGENTS:
                selected = AGENTS[choice]
                self.active_agent_key = selected["key"]
                print(f"\n✅ Agente ativo: {selected['label']}\n")
                return selected["key"]
              print("Opção inválida. Digite um número de 0 a 4.")
     
     def route(self, user_message: str) -> str:
         """
        Usa o LLM para identificar o agente correto com base na mensagem.
        Retorna a key do agente (ex: 'estatistica', 'ingles', etc).
        Usado apenas quando o agente ativo não está definido ou
        o usuário quer trocar de agente via comando natural.
        """
         response = self.llm.invoke([
            SystemMessage(content=SUPERVISOR_PROMPT),
            HumanMessage(content=user_message),
         ])

         raw = response.content.strip()

         # extrai a key do formato ROUTE:<key>
         if raw.startswith("ROUTE"):
             return raw.replace("ROUTE", "").strip()
         
         # fallback seguro
         return self.active_agent_key or "supervisor"
     
     def handle_switch_command(self, user_input: str) -> bool:
         """
        Verifica se o usuário quer trocar de agente.
        Comandos reconhecidos: 'trocar', 'menu', 'voltar', '/menu', '/trocar'
        Retorna True se o comando foi reconhecido e o menu foi exibido.
        """
         triggers = {"trocar", "menu", "voltar", "/menu", "/trocar", "mudar agente"}
         if user_input.lower().strip() in triggers:
             self.active_agent_key = None
             self.show_menu()
             return True
         return False
     
     def greet(self, agent_key: str) -> str:
         """Retorna a mensagem de boas-vindas para o agente selecionado."""
         greetings = {
            "estatistica": (
                "📐 Agente de Estatística ativo.\n"
                f"Hoje é {datetime.now().strftime('%d/%m/%Y')}. "
                "Pode perguntar sobre qualquer conteúdo das aulas, pedir resumos ou agendar revisões."
            ),
            "ingles": (
                "🇺🇸 English Agent active.\n"
                "I can give you writing exercises, correct your texts, "
                "or suggest YouTube channels and podcasts. What do you want to practice today?"
            ),
            "computacao": (
                "💻 Agente de Computação / IA ativo.\n"
                "Posso te ajudar com CS fundamentals, IA avançada, agentes, "
                "ou sugerir o próximo exercício do LeetCode."
            ),
            "aws": (
                "☁️  Agente AWS / Datacamp ativo.\n"
                "Posso registrar módulos concluídos, mostrar seu progresso "
                "ou responder dúvidas dos cursos."
            ),
        }
         return greetings.get(agent_key, "Agente ativo. Como posso ajudar?")