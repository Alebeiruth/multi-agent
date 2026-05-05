# Spec — Supervisor Agent

## Responsabilidade
Ponto de entrada do sistema. Exibe o menu de seleção de agente e mantém o estado do agente ativo durante a sessão.

## Comportamento

### Menu de seleção
Exibido uma vez ao iniciar o sistema. O usuário escolhe o agente pelo número (1–4). A escolha define o `active_agent_key` da sessão.

### Troca de agente
Comandos reconhecidos a qualquer momento: `trocar`, `menu`, `voltar`, `/menu`, `/trocar`. Exibe o menu novamente e reseta o `active_agent_key`.

### Roteamento via LLM
O método `route()` usa GPT-4o para identificar o agente correto a partir da mensagem. Retorna apenas `ROUTE:<key>` — sem texto adicional.

## Agentes disponíveis

| Número | Key | Agente |
|--------|-----|--------|
| 1 | `estatistica` | Estatística e Probabilidade |
| 2 | `ingles` | Inglês |
| 3 | `computacao` | Computação / IA / LeetCode |
| 4 | `aws` | AWS / Datacamp |

## Interface pública

```python
class Supervisor:
    def show_menu() -> str
    # Exibe menu e retorna a key do agente escolhido ou 'sair'

    def route(user_message: str) -> str
    # Retorna key do agente via LLM

    def handle_switch_command(user_input: str) -> bool
    # Retorna True se o input foi um comando de troca

    def greet(agent_key: str) -> str
    # Retorna mensagem de boas-vindas do agente
```

## Dependências
- `langchain_openai.ChatOpenAI` (GPT-4o)
- Nenhum storage próprio
- Nenhuma tool

## Restrições
- Nunca responde diretamente ao usuário com conteúdo de estudo
- Nunca invoca tools de outros agentes
- Não tem memória entre sessões