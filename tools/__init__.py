# ── Tools originais ───────────────────────────────────────────────────────
from .articles_tool import (
    adicionar_artigo,
    atualizar_status_artigo,
    consultar_artigo,
    listar_artigos,
)
from .aws_tool import (
    consultar_progresso_aws_datacamp,
    listar_duvidas_curso,
    registrar_duvida_curso,
    registrar_modulo_aws,
    registrar_modulo_datacamp,
    sugerir_proximo_aws_datacamp,
)
from .calendar_tool import agendar_sessao
from .computacao_tool import (
    consultar_progresso_computacao,
    listar_duvidas_pendentes,
    registrar_duvida,
    registrar_estudo_cs,
    sugerir_proximo_topico_cs,
)

# ── Tools novas ───────────────────────────────────────────────────────────
from .estatistica_tool import (
    calcular_revisoes,
    consultar_progresso_estatistica,
    gerar_conteudo_email_revisao,
    marcar_revisao_feita,
    registrar_aula,
)
from .gamification_tool import (
    consultar_dashboard_xp,
    registrar_xp_aws,
    registrar_xp_computacao,
)
from .ingles_tool import (
    adicionar_vocabulario,
    consultar_progresso_ingles,
    gerar_prompt_escrita,
    registrar_sessao_ingles,
    revisar_vocabulario,
    sugerir_conteudo_ingles,
)
from .leetcode_tool import (
    consultar_leetcode75,
    consultar_progresso,
    marcar_exercicio_leetcode75,
    proximo_leetcode75,
    registrar_exercicio,
    sugerir_proximo_exercicio,
)
from .rag_tool import rag_tool
