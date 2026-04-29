# 🎓 Multi-Agent Personal Study Coach

Sistema multi-agente de IA pessoal construído com LangGraph e GPT-4o para gerenciar múltiplos objetivos de estudo em paralelo. Um Supervisor roteia cada mensagem para o agente especialista correto, cada um com suas próprias tools, memória isolada e contexto específico.

---

## 🏗️ Arquitetura

```
multi-agent/
├── main.py                      # Ponto de entrada — menu + loop principal
├── agents/
│   ├── supervisor.py            # Roteamento por intenção + menu de seleção
│   ├── estatistica_agent.py     # Agente de Estatística e Probabilidade
│   ├── ingles_agent.py          # Agente de Inglês (imersão total)
│   ├── computacao_agent.py      # Agente de Computação / IA / LeetCode
│   └── aws_agent.py             # Agente de AWS SAA + Datacamp
├── tools/
│   ├── estatistica_tool.py      # RAG + revisões + Google Calendar + Gmail
│   ├── ingles_tool.py           # Exercícios, correção, vocabulário, sugestões
│   ├── computacao_tool.py       # CS roadmap, agentes, dúvidas técnicas
│   ├── aws_tool.py              # Tracking AWS SAA + Datacamp
│   ├── gamification_tool.py     # XP, níveis, streaks (AWS + Computação)
│   ├── leetcode_tool.py         # LeetCode 75 + exercícios livres
│   ├── calendar_tool.py         # Google Calendar (OAuth2)
│   ├── articles_tool.py         # Acervo de artigos científicos
│   └── rag_tool.py              # Busca semântica via ChromaDB
├── data/
│   └── articles/                # PDFs dos artigos e aulas
├── storage/
│   ├── estatistica.json         # Progresso das 8 aulas
│   ├── ingles.json              # Sessões, vocabulário
│   ├── computacao.json          # Estudos de CS e Agentes
│   ├── aws.json                 # Módulos AWS + Datacamp
│   ├── gamification.json        # XP, nível, streak
│   ├── leetcode75.json          # LeetCode 75 oficial
│   └── memory.db                # Memória SQLite (LangGraph)
├── chroma_db/                   # Índice vetorial — artigos
├── chroma_db_estatistica/       # Índice vetorial — aulas de estatística
├── credentials/                 # OAuth2 Google (não versionado)
├── .env                         # Chaves de API (não versionado)
└── ingest.py                    # Pipeline de indexação de PDFs
```

### Padrão de design

```
Usuário
  │
  ▼
Menu de seleção (1–4)
  │
  ▼
Supervisor Agent ──── GPT-4o · roteamento por intenção
  │
  ├──▶ Estatística Agent  ──  RAG · Calendar · Gmail MCP
  ├──▶ Inglês Agent       ──  imersão total · correção · vocabulário
  ├──▶ Computação Agent   ──  CS · LangGraph · LeetCode · gamificação
  └──▶ AWS Agent          ──  AWS SAA · Datacamp · gamificação
```

Cada agente tem `thread_id` isolado no SQLite — memória separada por domínio.

---

## 🤖 Agentes

### 📐 Estatística e Probabilidade
- Responde dúvidas com base nos PDFs das aulas via RAG
- Registra as 8 aulas e calcula automaticamente as 3 datas de revisão (D+0 quarta, D+3 sábado, D+5 segunda)
- Cria eventos no Google Calendar para cada revisão
- Envia emails de lembrete via Gmail MCP no dia da revisão
- Tracking de progresso das 8 aulas

### 🇺🇸 Inglês
- Imersão total — responde apenas em inglês
- Gera exercícios estruturados: email, essay, LinkedIn post, diálogo
- Corrige textos com metodologia: positivo → erros com explicação → texto corrigido → score 4 dimensões
- Salva vocabulário novo automaticamente durante a conversa
- Sugere canais do YouTube e podcasts por tema (tech, AI, business, daily)
- Tracking de horas de estudo por tipo de prática

### 💻 Computação / IA / LeetCode
- Cobre CS fundamentals e padrões de design de agentes (LangGraph, ReAct, Supervisor, MCP)
- Roadmap estruturado: 18 tópicos de CS + 14 de Agentes em ordem pedagógica
- LeetCode 75 integrado: marca exercícios, sugere o próximo, consulta progresso por tópico
- Explica soluções: naive → otimizada → complexidade
- Registra dúvidas técnicas para revisão futura
- **Gamificação:** XP por tópico e exercício · níveis · streaks com multiplicadores

### ☁️ AWS / Datacamp
- Tracking do curso AWS Solutions Architect Associate (SAA-C03) — roadmap de 32 tópicos
- Tracking de 4 trilhas Datacamp: Python, Machine Learning, Data Engineering, AI & LLMs
- Explica serviços AWS com foco no exame: o que é → quando usar → pegadinhas do SAA-C03
- Agenda sessões no Google Calendar
- **Gamificação:** XP por módulo concluído · níveis · streaks com multiplicadores

---

## 🎮 Sistema de Gamificação (AWS + Computação)

| Título | XP |
|--------|----|
| Noob | 0 – 300 |
| Aprendiz | 300 – 800 |
| Witcher | 800 – 1.800 |
| Black Witcher | 1.800 – 3.500 |
| The Lich King | 3.500+ |

**Tabela de XP:**

| Ação | XP |
|------|----|
| Tópico AWS concluído | +30 |
| Sessão de estudo AWS | +20 |
| Módulo Datacamp | +25 |
| Tópico CS / Agentes | +20 |
| LeetCode easy | +10 |
| LeetCode medium | +20 |
| LeetCode hard | +40 |
| Bônus streak 7 dias | +50 |

**Multiplicadores de streak:** ×1.5 (14d) · ×2.0 (30d) · ×3.0 (60d)
**Freeze day:** 1 pausa por semana sem quebrar o streak.

---

## 🛠️ Stack Técnica

| Camada | Tecnologia |
|--------|-----------|
| Orquestração | LangGraph 1.0 + LangChain 0.3 |
| LLM | GPT-4o (OpenAI) |
| Embedding | BAAI/bge-large-en-v1.5 (HuggingFace) |
| Vector Store | ChromaDB |
| Memória | AsyncSqliteSaver (LangGraph) |
| MCP | mcp-google-calendar · mcp-gmail |
| Calendário | Google Calendar API (OAuth2) |
| Email | Gmail MCP |
| Extração de PDF | PyMuPDF (fitz) |

---

## 🚀 Instalação

### Pré-requisitos
- Python 3.11+
- Node.js 18+ (para os MCP Servers)
- Conta Google com Calendar API e Gmail API habilitadas

### 1. Clone o repositório

```bash
git clone https://github.com/Alebeiruth/multi-agent.git
cd multi-agent
```

### 2. Ambiente virtual e dependências

```bash
python -m virtualenv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
pip install langchain-openai langchain-mcp-adapters langgraph-checkpoint-sqlite
```

### 3. Configure o `.env`

Crie `.env` na raiz do projeto:

```env
OPENAI_API_KEY=sua_chave_aqui
ALEXANDRE_EMAIL=seu@email.com

# Opcional — monitoramento com LangSmith
# LANGCHAIN_TRACING_V2=true
# LANGCHAIN_API_KEY=sua_chave_aqui
# LANGCHAIN_PROJECT=multi-agent-coach
```

### 4. Configure o Google (Calendar + Gmail)

1. Acesse [console.cloud.google.com](https://console.cloud.google.com)
2. Crie um projeto e ative **Google Calendar API** e **Gmail API**
3. Crie credenciais OAuth2 — tipo **Desktop App**
4. Salve em `credentials/google_credentials.json`
5. Gere o token:

```bash
python -c "
from google_auth_oauthlib.flow import InstalledAppFlow
SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/gmail.send',
]
flow = InstalledAppFlow.from_client_secrets_file('credentials/google_credentials.json', SCOPES)
creds = flow.run_local_server(port=0)
with open('credentials/token_python.json', 'w') as f:
    f.write(creds.to_json())
"
```

### 5. Indexe os PDFs

Coloque os PDFs em `data/articles/` e rode:

```bash
python ingest.py
```

Para os PDFs das aulas de estatística, crie `data/estatistica/` e adapte o `ingest.py` apontando para `chroma_db_estatistica`.

### 6. Rode o sistema

```bash
python main.py
```

---

## 🗺️ Roadmap de Implementação

### ✅ Fase 1 — Agentes (concluída)
- [x] Supervisor com menu de seleção e roteamento por intenção
- [x] Agente de Estatística — RAG + revisões + Calendar + Gmail
- [x] Agente de Inglês — imersão total + correção + vocabulário
- [x] Agente de Computação — CS + Agentes + LeetCode
- [x] Agente AWS — SAA tracking + Datacamp + Calendar
- [x] Sistema de gamificação — XP + níveis + streaks (AWS + Computação)

### 🔄 Fase 2 — Qualidade e Observabilidade
- [ ] **Pydantic** — validação de inputs/outputs em todas as tools
- [ ] **LangSmith** — tracing de todas as chamadas de agente
- [ ] **Pytest** — testes unitários por tool e por agente
- [ ] **Ruff** — lint e formatação de código
- [ ] **GitHub Actions** — CI: roda pytest + ruff em todo push
- [ ] **Pasta `specs/`** — contrato de cada agente (inputs, outputs, tools)

### 🔮 Fase 3 — Features Avançadas
- [ ] **RAGAS** — avaliação de qualidade do RAG de Estatística
- [ ] **E2B via MCP** — execução de código LeetCode em sandbox isolado
- [ ] **Dashboard web** — visualização de XP, streaks e progresso (FastAPI + React)
- [ ] **Notificações proativas** — agente verifica agenda e manda lembretes sem ser perguntado

---

## 📝 Licença

MIT