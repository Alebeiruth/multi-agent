# ── Tools originais ───────────────────────────────────────────────────────
from .rag_tool import rag_tool
from .articles_tool import listar_artigos, atualizar_status_artigo, adicionar_artigo, consultar_artigo
from .leetcode_tool import (
    registrar_exercicio,
    consultar_progresso,
    sugerir_proximo_exercicio,
    consultar_leetcode75,
    marcar_exercicio_leetcode75,
    proximo_leetcode75,
)
from .calendar_tool import agendar_sessao

# ── Tools novas ───────────────────────────────────────────────────────────
from .estatistica_tool import (
    registrar_aula,
    consultar_progresso_estatistica,
    calcular_revisoes,
    marcar_revisao_feita,
    gerar_conteudo_email_revisao,
)
from .ingles_tool import (
    registrar_sessao_ingles,
    consultar_progresso_ingles,
    adicionar_vocabulario,
    revisar_vocabulario,
    sugerir_conteudo_ingles,
    gerar_prompt_escrita,
)
from .computacao_tool import (
    registrar_estudo_cs,
    consultar_progresso_computacao,
    sugerir_proximo_topico_cs,
    registrar_duvida,
    listar_duvidas_pendentes,
)
from .aws_tool import (
    registrar_modulo_aws,
    registrar_modulo_datacamp,
    consultar_progresso_aws_datacamp,
    sugerir_proximo_aws_datacamp,
    registrar_duvida_curso,
    listar_duvidas_curso,
)
from .gamification_tool import (
    registrar_xp_aws,
    registrar_xp_computacao,
    consultar_dashboard_xp,
)