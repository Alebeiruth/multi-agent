# Spec — AWS / Datacamp Agent

## Responsabilidade
Tracking do curso AWS Solutions Architect Associate (SAA-C03) e trilhas do Datacamp. Responde dúvidas técnicas com foco no exame, agenda sessões e gamifica o progresso.

## Contexto
- Certificação alvo: AWS SAA-C03
- Plataformas: Udemy (AWS) + Datacamp
- Idioma: Português
- Memória: `thread_id = "alexandre-aws"`
- Temperatura LLM: 0

## Tools disponíveis

| Tool | Descrição | Quando usar |
|------|-----------|-------------|
| `registrar_modulo_aws` | Loga tópico AWS concluído | Usuário terminou um tópico AWS |
| `registrar_modulo_datacamp` | Loga módulo Datacamp concluído | Usuário terminou módulo no Datacamp |
| `consultar_progresso_aws_datacamp` | Progresso unificado de ambos os cursos | Usuário pergunta sobre progresso |
| `sugerir_proximo_aws_datacamp` | Próximo tópico por plataforma | Usuário pede sugestão do que estudar |
| `registrar_duvida_curso` | Salva dúvida técnica | Conceito ficou em aberto |
| `listar_duvidas_curso` | Lista dúvidas pendentes | Início de sessão ou revisão |
| `agendar_sessao` | Cria evento no Google Calendar | Usuário quer agendar sessão |
| `registrar_xp_aws` | Registra XP e exibe dashboard | Sempre após registrar módulo |
| `consultar_dashboard_xp` | Dashboard completo de XP | Usuário pergunta sobre pontos |

## Roadmap AWS SAA (32 tópicos)
Cloud Computing → IAM → EC2 (4 tópicos) → S3 (4 tópicos) → RDS (2 tópicos) → ElastiCache → DynamoDB → VPC (3 tópicos) → Route 53 → CloudFront → SQS → SNS → Lambda → API Gateway → CloudWatch → CloudTrail → KMS → WAF/Shield → Well-Architected (4 tópicos)

## Trilhas Datacamp

| Trilha | Módulos |
|--------|---------|
| Python | 5 módulos |
| Machine Learning | 5 módulos |
| Data Engineering | 4 módulos |
| AI & LLMs | 4 módulos |

## XP por ação
| Ação | XP |
|------|----|
| Tópico AWS concluído | +30 |
| Sessão de estudo AWS | +20 |
| Módulo Datacamp | +25 |

## Metodologia para dúvidas AWS
1. O que é (definição precisa)
2. Quando usar (casos de uso reais)
3. Como funciona por baixo (arquitetura simplificada)
4. Pegadinhas do exame SAA-C03
5. Diferença de serviços similares

## Storage
- Arquivo: `storage/aws/aws.json`
- Schema:
```json
{
  "modulos_aws": [
    {
      "topico": "string",
      "duracao_minutos": 60,
      "status": "concluido | revisando | com_duvidas",
      "observacoes": "string",
      "data": "YYYY-MM-DD"
    }
  ],
  "modulos_datacamp": [
    {
      "curso": "Python | Machine Learning | Data Engineering | AI & LLMs",
      "modulo": "string",
      "duracao_minutos": 30,
      "status": "concluido | em_andamento | revisando",
      "observacoes": "string",
      "data": "YYYY-MM-DD"
    }
  ],
  "duvidas": [
    {
      "plataforma": "aws | datacamp",
      "topico": "string",
      "duvida": "string",
      "resolvida": false,
      "data": "YYYY-MM-DD"
    }
  ]
}
```

## Validações (Pydantic)
- `status` AWS: `concluido`, `revisando` ou `com_duvidas`
- `status` Datacamp: `concluido`, `em_andamento` ou `revisando`
- `curso`: literal enum das 4 trilhas
- `plataforma`: `aws` ou `datacamp`
- `duracao_minutos`: 1–480

## Dependências externas
- Google Calendar MCP (`create_event`)
- OpenAI GPT-4o

## Restrições
- NUNCA inventar comportamentos de serviços AWS
- Sempre avisar quando preços ou limites puderem ter mudado
- Focar no que cai no SAA-C03 nas explicações técnicas