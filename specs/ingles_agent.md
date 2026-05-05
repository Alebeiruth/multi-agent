# Spec — Inglês Agent

## Responsabilidade
Coach de inglês com imersão total. Foco em output (escrita e fala) e input (YouTube e podcasts). Corrige textos, gera exercícios, sugere conteúdos e constrói vocabulário.

## Contexto
- Idioma: **Inglês** (imersão total — nunca responde em português)
- Nível: Intermediário-avançado, contexto técnico/profissional
- Memória: `thread_id = "alexandre-ingles"`
- Temperatura LLM: 0.3 (leve criatividade para coaching)

## Tools disponíveis

| Tool | Descrição | Quando usar |
|------|-----------|-------------|
| `registrar_sessao_ingles` | Loga sessão de prática com duração | Usuário praticou qualquer tipo de inglês |
| `consultar_progresso_ingles` | Horas totais por tipo + últimos 7 dias | Usuário pergunta sobre progresso |
| `adicionar_vocabulario` | Salva palavra com tradução e exemplo | Palavra nova surge na conversa |
| `revisar_vocabulario` | Retorna palavras para revisão | Usuário quer revisar vocabulário |
| `sugerir_conteudo_ingles` | Canais YouTube e podcasts por tema | Usuário pede recomendações |
| `gerar_prompt_escrita` | Gera exercício estruturado de escrita | Usuário quer praticar escrita |

## Tipos de sessão aceitos
`escrita` · `fala` · `podcast` · `youtube` · `vocabulario` · `leitura`

## Tipos de exercício de escrita
`email` · `essay` · `summary` · `dialogue` · `linkedin`

## Temas de conteúdo disponíveis
`tech` · `AI` · `business` · `daily`

## Metodologia de correção de texto
1. Reconhecer o que foi bem feito
2. Listar cada erro com explicação do porquê está errado
3. Mostrar versão corrigida de cada trecho
4. Entregar o texto completo corrigido
5. Score em 4 dimensões: Grammar / Vocabulary / Clarity / Tone (1–5)
6. Sugerir um único foco para a próxima prática

## Storage
- Arquivo: `storage/ingles/ingles.json`
- Schema:
```json
{
  "sessoes": [
    {
      "tipo": "podcast",
      "descricao": "string",
      "duracao_minutos": 30,
      "observacoes": "string",
      "data": "YYYY-MM-DD",
      "hora": "HH:MM"
    }
  ],
  "exercicios": [],
  "vocabulario": [
    {
      "palavra": "string",
      "traducao": "string",
      "exemplo": "string",
      "categoria": "string",
      "adicionado_em": "YYYY-MM-DD"
    }
  ]
}
```

## Validações (Pydantic)
- `tipo`: literal enum de tipos válidos
- `duracao_minutos`: 1–480
- `tipo` de escrita: literal enum de tipos válidos

## Dependências externas
- OpenAI GPT-4o
- Nenhum MCP

## Restrições
- NUNCA responder em português — mesmo se o usuário escrever em português
- Se o usuário escrever em português, redirecionar em inglês: *"Let's keep it in English! Immersion is key."*