# Spec — Computação / IA / LeetCode Agent

## Responsabilidade
Cobrir três frentes: CS Fundamentals, padrões de design de Agentes/LangGraph e prática de LeetCode. Tracking de progresso, resposta a dúvidas técnicas e gamificação.

## Contexto
- Idioma: Português
- Linguagem de código padrão: Python
- Memória: `thread_id = "alexandre-computacao"`
- Temperatura LLM: 0

## Tools disponíveis

### CS e Agentes
| Tool | Descrição | Quando usar |
|------|-----------|-------------|
| `registrar_estudo_cs` | Loga sessão de estudo por área e tópico | Usuário estudou um tópico |
| `consultar_progresso_computacao` | Progresso por área com % e pendentes | Usuário pergunta sobre progresso |
| `sugerir_proximo_topico_cs` | Próximo tópico do roadmap | Usuário pede sugestão do que estudar |
| `registrar_duvida` | Salva dúvida técnica para revisão | Conceito ficou em aberto |
| `listar_duvidas_pendentes` | Lista dúvidas não resolvidas | Início de sessão ou revisão |

### LeetCode (reuso das tools originais)
| Tool | Descrição | Quando usar |
|------|-----------|-------------|
| `marcar_exercicio_leetcode75` | Marca exercício do LeetCode 75 | Exercício da lista oficial |
| `registrar_exercicio` | Registra exercício livre | Exercício fora do LeetCode 75 |
| `proximo_leetcode75` | Próximo exercício pendente | Usuário pede próximo da lista |
| `consultar_leetcode75` | Progresso por tópico | Usuário pergunta sobre LeetCode 75 |
| `consultar_progresso` | Progresso geral de exercícios livres | Histórico de exercícios |
| `sugerir_proximo_exercicio` | Sugestão baseada no histórico | Usuário pede sugestão livre |

### Gamificação
| Tool | Descrição | Quando usar |
|------|-----------|-------------|
| `registrar_xp_computacao` | Registra XP e exibe dashboard | Sempre após registrar estudo ou LeetCode |
| `consultar_dashboard_xp` | Dashboard completo de XP | Usuário pergunta sobre pontos |

## Roadmap — CS Fundamentals (18 tópicos)
Arrays e Strings → Linked Lists → Stacks e Queues → Hash Tables → Trees e BST → Graphs → Heaps → Sorting e Searching → Recursão e Backtracking → Dynamic Programming → Complexidade (Big-O) → OS Processos/Threads → OS Memória → Redes TCP/IP → Redes DNS/CDN → BD SQL → BD Índices → Compiladores

## Roadmap — Agentes (14 tópicos)
LLMs Transformer → Prompt Engineering → Function Calling → RAG → Embeddings → LangChain Chains → LangGraph Grafos → LangGraph Checkpointer → ReAct Agent → Supervisor Pattern → Plan and Execute → MCP → Avaliação → Deploy

## XP por ação
| Ação | XP |
|------|----|
| Tópico CS ou Agentes | +20 |
| LeetCode easy | +10 |
| LeetCode medium | +20 |
| LeetCode hard | +40 |

## Storage
- Arquivo: `storage/computacao/computacao.json`
- Schema:
```json
{
  "estudos": [
    {
      "area": "cs_fundamentals | agentes",
      "topico": "string",
      "duracao_minutos": 60,
      "status": "estudado | revisando | dominado",
      "observacoes": "string",
      "data": "YYYY-MM-DD"
    }
  ],
  "duvidas": [
    {
      "area": "cs_fundamentals | agentes",
      "topico": "string",
      "duvida": "string",
      "resolvida": false,
      "data": "YYYY-MM-DD"
    }
  ]
}
```

## Metodologia de explicação técnica
1. Conceito em uma frase
2. Por que importa na prática
3. Exemplo em Python
4. Casos extremos e armadilhas
5. Conexão com outros tópicos do roadmap

## Validações (Pydantic)
- `area`: `cs_fundamentals` ou `agentes`
- `status`: `estudado`, `revisando` ou `dominado`
- `duracao_minutos`: 1–480

## Dependências externas
- OpenAI GPT-4o
- Nenhum MCP

## Restrições
- NUNCA inventar APIs ou comportamentos de bibliotecas
- Código sempre em Python salvo pedido explícito
- Para LeetCode 75: usar `marcar_exercicio_leetcode75`, não `registrar_exercicio`