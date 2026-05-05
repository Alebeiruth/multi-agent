# Spec — Estatística Agent

## Responsabilidade
Auxiliar Alexandre nas 8 aulas de Estatística e Probabilidade: responder dúvidas via RAG, registrar aulas, calcular revisões e enviar lembretes via Google Calendar e Gmail.

## Contexto
- Total de aulas: 8, todas às quartas-feiras
- Padrão de revisão: D+0 (quarta), D+3 (sábado), D+5 (segunda)
- Idioma: Português
- Memória: `thread_id = "alexandre-estatistica"`

## Tools disponíveis

| Tool | Descrição | Quando usar |
|------|-----------|-------------|
| `buscar_conteudo_aula` | RAG sobre PDFs das aulas | Dúvidas sobre fórmulas, conceitos, exemplos |
| `registrar_aula` | Salva aula no storage | Usuário diz que assistiu uma aula |
| `consultar_progresso_estatistica` | Progresso das 8 aulas | Usuário pergunta quantas aulas faltam |
| `calcular_revisoes` | Retorna as 3 datas de revisão | Antes de agendar no Calendar |
| `marcar_revisao_feita` | Marca revisão como concluída | Usuário diz que fez uma revisão |
| `gerar_conteudo_email_revisao` | Monta assunto e corpo do email | Antes de enviar via Gmail MCP |
| `agendar_sessao` | Cria evento no Google Calendar | Após calcular datas de revisão |
| `send_email` (Gmail MCP) | Envia email de lembrete | Após gerar conteúdo do email |

## Fluxo ao registrar uma aula nova

```
registrar_aula
    └── calcular_revisoes
            ├── agendar_sessao (revisão 1)
            ├── agendar_sessao (revisão 2)
            ├── agendar_sessao (revisão 3)
            ├── gerar_conteudo_email_revisao (revisão 1) → send_email
            ├── gerar_conteudo_email_revisao (revisão 2) → send_email
            └── gerar_conteudo_email_revisao (revisão 3) → send_email
```

## Storage
- Arquivo: `storage/estatistica/estatistica.json`
- Schema:
```json
{
  "aulas": [
    {
      "numero": 1,
      "tema": "string",
      "conteudos": "string",
      "data_aula": "YYYY-MM-DD",
      "observacoes": "string",
      "revisoes": {
        "revisao_1": "YYYY-MM-DD HH:MM",
        "revisao_2": "YYYY-MM-DD HH:MM",
        "revisao_3": "YYYY-MM-DD HH:MM"
      },
      "revisoes_feitas": [1, 2],
      "registrado_em": "YYYY-MM-DD HH:MM"
    }
  ],
  "total_aulas": 8
}
```

## RAG
- ChromaDB: `./chroma_db_estatistica`
- Collection: `estatistica`
- Embeddings: `BAAI/bge-large-en-v1.5`
- PDFs: `data/estatistica/`
- k: 4 chunks por query

## Validações (Pydantic)
- `numero`: 1–8
- `data_aula`: formato `YYYY-MM-DD`
- `numero_revisao`: 1–3

## Dependências externas
- Google Calendar MCP (`create_event`)
- Gmail MCP (`send_email`)
- OpenAI GPT-4o
- HuggingFace `BAAI/bge-large-en-v1.5`
- ChromaDB

## Restrições
- NUNCA inventar fórmulas ou definições — usar sempre `buscar_conteudo_aula`
- Se PDF não estiver indexado, avisar para rodar `ingest.py --colecao estatistica`