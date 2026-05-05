# Spec — Sistema de Gamificação

## Responsabilidade
Registrar XP, calcular níveis, manter streaks e exibir dashboard inline no chat. Ativo apenas nos agentes de Computação e AWS.

## Níveis

| Título | XP mínimo | XP máximo |
|--------|-----------|-----------|
| Noob | 0 | 299 |
| Aprendiz | 300 | 799 |
| Witcher | 800 | 1.799 |
| Black Witcher | 1.800 | 3.499 |
| The Lich King | 3.500 | ∞ |

## Tabela de XP

| Ação | XP base |
|------|---------|
| Tópico AWS concluído | +30 |
| Sessão de estudo AWS | +20 |
| Módulo Datacamp | +25 |
| Tópico CS Fundamentals | +20 |
| Tópico Agentes | +20 |
| LeetCode easy | +10 |
| LeetCode medium | +20 |
| LeetCode hard | +40 |
| Bônus streak 7 dias | +50 |

## Multiplicadores de streak

| Streak | Multiplicador |
|--------|--------------|
| 1–13 dias | ×1.0 |
| 14–29 dias | ×1.5 |
| 30–59 dias | ×2.0 |
| 60+ dias | ×3.0 |

O multiplicador é aplicado sobre o XP base antes de somar ao total.

## Freeze day
- 1 pausa por semana sem quebrar o streak
- Ativado automaticamente se o último estudo foi há 2 dias e o freeze não foi usado na semana
- Reseta toda semana (baseado em `isocalendar()[1]`)

## Bônus de streak
- A cada múltiplo de 7 dias de streak, +50 XP bonus

## Dashboard inline
Exibido automaticamente após cada `registrar_xp_aws` ou `registrar_xp_computacao`:

```
════════════════════════════════════════
  +30 XP  —  IAM — Policies concluído
────────────────────────────────────────
  Witcher  •  850 XP total
  ██░░░░░░░░ 5%
  950 XP para Black Witcher
  🔥 Streak: 14 dia(s)  •  Máximo: 14
════════════════════════════════════════
```

## Storage
- Arquivo: `storage/gamification/gamification.json`
- Schema:
```json
{
  "xp_total": 0,
  "xp_aws": 0,
  "xp_computacao": 0,
  "nivel_atual": "Noob",
  "streak_atual": 0,
  "streak_maximo": 0,
  "ultimo_dia_estudo": "YYYY-MM-DD",
  "freeze_usado_semana": false,
  "ultima_semana_freeze": null,
  "historico": [
    {
      "data": "YYYY-MM-DD HH:MM",
      "area": "aws | computacao",
      "tipo": "string",
      "descricao": "string",
      "xp_base": 30,
      "multiplicador": 1.5,
      "xp_ganho": 45,
      "streak": 14
    }
  ]
}
```

## Tools

| Tool | Input | Output |
|------|-------|--------|
| `registrar_xp_aws` | `tipo`, `descricao` | Dashboard formatado |
| `registrar_xp_computacao` | `tipo`, `descricao`, `dificuldade?` | Dashboard formatado |
| `consultar_dashboard_xp` | — | Dashboard completo com histórico |

## Validações (Pydantic)
- `tipo` AWS: `aws_topico`, `aws_sessao`, `datacamp_modulo`
- `tipo` CS: `cs_topico`, `agentes_topico`, `leetcode_easy`, `leetcode_medium`, `leetcode_hard`
- `dificuldade`: `easy`, `medium`, `hard` ou vazio

## Restrições
- XP é acumulativo e nunca decresce
- Streak zera se passar mais de 1 dia sem estudar (exceto freeze day)
- O dashboard é sempre exibido inline — não requer comando do usuário