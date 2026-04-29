import json
import os
from datetime import datetime, date, timedelta
from langchain_core.tools import tool

STORAGE_FILE = "storage/gamification.json"

# ── Configuração do sistema ────────────────────────────────────────────────

NIVEIS = [
    {"titulo": "Noob",          "min": 0,    "max": 300},
    {"titulo": "Aprendiz",      "min": 300,  "max": 800},
    {"titulo": "Witcher",       "min": 800,  "max": 1800},
    {"titulo": "Black Witcher", "min": 1800, "max": 3500},
    {"titulo": "The Lich King", "min": 3500, "max": float("inf")},
]

XP_TABLE = {
     # AWS
    "aws_topico":           30,
    "aws_sessao":           20,
    # Datacamp
    "datacamp_modulo":      25,
    # CS / Agentes
    "cs_topico":            20,
    "agentes_topico":       20,
    # LeetCode
    "leetcode_easy":        10,
    "leetcode_medium":      20,
    "leetcode_hard":        40,
    # Streak
    "streak_7d":            50,
}

STREAK_MULTIPLICADORES = [
    (60, 3.0),
    (30, 2.0),
    (14, 1.5),
    (1,  1.0),
]

MENSAGENS_NIVEL = {
    "Noob":          "Bem-vindo à jornada, novato. Todo mestre já foi um noob.",
    "Aprendiz":      "Você cruzou o primeiro portal. O conhecimento começa a tomar forma.",
    "Witcher":       "As habilidades se afiaram. Você é um Witcher — bruxo das complexidades.",
    "Black Witcher": "Poucos chegam aqui. A escuridão do conhecimento avançado não te assusta mais.",
    "The Lich King": "Você transcendeu. O domínio é total. A morte do ignorante chegou.",
}

# ── Helpers ────────────────────────────────────────────────────────────────

def _load() -> dict:
    if not os.path.exists(STORAGE_FILE):
        return {
            "xp_total": 0,
            "xp_aws": 0,
            "xp_computacao": 0,
            "nivel_atual": "Noob",
            "streak_atual": 0,
            "streak_maximo": 0,
            "ultimo_dia_estudo": None,
            "freeze_usado_semana": False,
            "ultima_semana_freeze": None,
            "historico": [],
        }
    with open(STORAGE_FILE, "r", encoding="utf-8") as f:
        content = f.read().strip()
        if not content:
            return _load.__wrapped__() if hasattr(_load, '__wrapped__') else {}
        return json.loads(content)
    
def _save(data: dict):
    os.makedirs("storage", exist_ok=True)
    with open(STORAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
 
 
def _get_nivel(xp: int) -> dict:
    for nivel in reversed(NIVEIS):
        if xp >= nivel["min"]:
            return nivel
    return NIVEIS[0]
 
 
def _get_multiplicador(streak: int) -> float:
    for dias, mult in STREAK_MULTIPLICADORES:
        if streak >= dias:
            return mult
    return 1.0

def _atualizar_streak(data: dict) -> tuple[int, bool, bool]:
    """
    Atualiza o streak com base na data de hoje.
    Retorna (streak_atual, subiu_de_nivel, ganhou_bonus_streak).
    """
    hoje = date.today().isoformat()
    ultimo = data.get("ultimo_dia_estudo")
    streak = data.get("streak_atual", 0)
    bonus_streak = False
 
    if ultimo is None:
        streak = 1
    elif ultimo == hoje:
        pass  # já estudou hoje, não altera
    else:
        ontem = (date.today() - timedelta(days=1)).isoformat()
        if ultimo == ontem:
            streak += 1
        else:
            # verificar freeze
            semana_atual = date.today().isocalendar()[1]
            semana_freeze = data.get("ultima_semana_freeze")
            freeze_usado = data.get("freeze_usado_semana", False)
 
            # reset semanal do freeze
            if semana_freeze != semana_atual:
                data["freeze_usado_semana"] = False
                data["ultima_semana_freeze"] = semana_atual
                freeze_usado = False
 
            dias_perdidos = (date.today() - date.fromisoformat(ultimo)).days
            if dias_perdidos == 2 and not freeze_usado:
                # usa freeze day automaticamente
                data["freeze_usado_semana"] = True
                data["ultima_semana_freeze"] = semana_atual
                streak += 1
            else:
                streak = 1  # streak quebrado
 
    data["streak_atual"] = streak
    data["ultimo_dia_estudo"] = hoje
 
    if streak > data.get("streak_maximo", 0):
        data["streak_maximo"] = streak
 
    # bônus de 7 dias
    if streak > 0 and streak % 7 == 0:
        bonus_streak = True
 
    return streak, bonus_streak


def _barra_progresso(xp: int, nivel: dict) -> str:
    """Gera uma barra de progresso ASCII para o nível atual."""
    if nivel["max"] == float("inf"):
        return "██████████ MAX"
    xp_no_nivel = xp - nivel["min"]
    total_nivel = nivel["max"] - nivel["min"]
    pct = min(xp_no_nivel / total_nivel, 1.0)
    blocos = int(pct * 10)
    barra = "█" * blocos + "░" * (10 - blocos)
    return f"{barra} {int(pct * 100)}%"
 
 
def _registrar_xp(area: str, tipo: str, xp_base: int, descricao: str) -> str:
    """
    Função central de registro de XP.
    Usada por todas as tools de gamificação.
    Retorna o dashboard formatado para exibir no chat.
    """
    data = _load()
 
    # atualiza streak
    streak, bonus_streak = _atualizar_streak(data)
    mult = _get_multiplicador(streak)
 
    # calcula XP final com multiplicador
    xp_ganho = int(xp_base * mult)
    xp_bonus_streak = XP_TABLE["streak_7d"] if bonus_streak else 0
 
    xp_total_anterior = data["xp_total"]
    nivel_anterior = _get_nivel(xp_total_anterior)
 
    # soma XP
    data["xp_total"] += xp_ganho + xp_bonus_streak
    if area == "aws":
        data["xp_aws"] = data.get("xp_aws", 0) + xp_ganho
    elif area == "computacao":
        data["xp_computacao"] = data.get("xp_computacao", 0) + xp_ganho
 
    # verifica mudança de nível
    nivel_novo = _get_nivel(data["xp_total"])
    subiu_nivel = nivel_novo["titulo"] != nivel_anterior["titulo"]
    data["nivel_atual"] = nivel_novo["titulo"]
 
    # registra no histórico
    data["historico"].append({
        "data": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "area": area,
        "tipo": tipo,
        "descricao": descricao,
        "xp_base": xp_base,
        "multiplicador": mult,
        "xp_ganho": xp_ganho,
        "streak": streak,
    })
 
    _save(data)
 
    # ── Monta dashboard ───────────────────────────────────────────────────
    barra = _barra_progresso(data["xp_total"], nivel_novo)
    xp_proximo = (
        f"{nivel_novo['max'] - data['xp_total']} XP para {NIVEIS[NIVEIS.index(nivel_novo) + 1]['titulo']}"
        if nivel_novo["max"] != float("inf")
        else "nível máximo atingido"
    )
 
    streak_emoji = "🔥" if streak >= 7 else "⚡" if streak >= 3 else "✨"
    mult_str = f" (×{mult})" if mult > 1.0 else ""
 
    dashboard = (
        f"\n{'═' * 40}\n"
        f"  +{xp_ganho} XP{mult_str}  —  {descricao}\n"
    )
 
    if bonus_streak:
        dashboard += f"  +{xp_bonus_streak} XP  —  bônus streak {streak} dias!\n"
 
    dashboard += (
        f"{'─' * 40}\n"
        f"  {nivel_novo['titulo']}  •  {data['xp_total']} XP total\n"
        f"  {barra}\n"
        f"  {xp_proximo}\n"
        f"  {streak_emoji} Streak: {streak} dia(s)  •  Máximo: {data['streak_maximo']}\n"
    )
 
    if subiu_nivel:
        dashboard += (
            f"{'═' * 40}\n"
            f"  LEVEL UP!  {nivel_anterior['titulo']} → {nivel_novo['titulo']}\n"
            f"  {MENSAGENS_NIVEL[nivel_novo['titulo']]}\n"
        )
 
    dashboard += f"{'═' * 40}\n"
 
    return dashboard
 
 
# ── Tool 1: registrar XP de AWS ───────────────────────────────────────────
 
@tool
def registrar_xp_aws(tipo: str, descricao: str) -> str:
    """
    Registra XP ganho em uma atividade de AWS ou Datacamp.
    Chame SEMPRE após registrar um módulo AWS ou Datacamp concluído.
 
    Args:
        tipo: Tipo da atividade.
              Valores: 'aws_topico', 'aws_sessao', 'datacamp_modulo'.
        descricao: Descrição curta do que foi feito. Exemplo: 'IAM — Policies concluído'.
 
    Returns:
        Dashboard com XP ganho, nível atual, barra de progresso e streak.
    """
    xp_base = XP_TABLE.get(tipo, 20)
    return _registrar_xp("aws", tipo, xp_base, descricao)
 
 
# ── Tool 2: registrar XP de Computação ───────────────────────────────────
 
@tool
def registrar_xp_computacao(tipo: str, descricao: str, dificuldade: str = "") -> str:
    """
    Registra XP ganho em uma atividade de Computação, IA ou LeetCode.
    Chame SEMPRE após registrar um tópico de CS/Agentes ou exercício LeetCode.
 
    Args:
        tipo: Tipo da atividade.
              Valores: 'cs_topico', 'agentes_topico',
                       'leetcode_easy', 'leetcode_medium', 'leetcode_hard'.
        descricao: Descrição curta. Exemplo: 'LeetCode — Two Sum resolvido'.
        dificuldade: Apenas para LeetCode: 'easy', 'medium' ou 'hard'.
                     Deixe vazio para outros tipos.
 
    Returns:
        Dashboard com XP ganho, nível atual, barra de progresso e streak.
    """
    if dificuldade and tipo == "leetcode_easy":
        tipo = f"leetcode_{dificuldade}"
 
    xp_base = XP_TABLE.get(tipo, 20)
    return _registrar_xp("computacao", tipo, xp_base, descricao)
 
 
# ── Tool 3: consultar dashboard completo ──────────────────────────────────
 
@tool
def consultar_dashboard_xp() -> str:
    """
    Exibe o dashboard completo de gamificação com XP, nível, streak e histórico recente.
    Use quando o usuário perguntar sobre seus pontos, nível ou progresso de gamificação.
 
    Returns:
        Dashboard completo formatado.
    """
    data = _load()
 
    if data["xp_total"] == 0:
        return (
            "Nenhum XP registrado ainda.\n"
            "Comece estudando um tópico e os pontos aparecerão automaticamente!"
        )
 
    nivel = _get_nivel(data["xp_total"])
    barra = _barra_progresso(data["xp_total"], nivel)
    streak = data.get("streak_atual", 0)
    streak_emoji = "🔥" if streak >= 7 else "⚡" if streak >= 3 else "✨"
 
    xp_proximo = (
        f"{nivel['max'] - data['xp_total']} XP para {NIVEIS[NIVEIS.index(nivel) + 1]['titulo']}"
        if nivel["max"] != float("inf")
        else "nível máximo atingido"
    )
 
    # histórico recente (últimas 5 ações)
    historico = data.get("historico", [])[-5:]
    hist_str = "\n".join(
        f"  • {h['data'][:10]} +{h['xp_ganho']} XP — {h['descricao']}"
        for h in reversed(historico)
    ) or "  Nenhuma atividade ainda."
 
    mult = _get_multiplicador(streak)
    mult_str = f"×{mult} ativo" if mult > 1.0 else "sem multiplicador"
 
    return (
        f"\n{'═' * 44}\n"
        f"  DASHBOARD DE GAMIFICAÇÃO\n"
        f"{'─' * 44}\n"
        f"  Título:    {nivel['titulo']}\n"
        f"  XP Total:  {data['xp_total']}\n"
        f"  AWS XP:    {data.get('xp_aws', 0)}\n"
        f"  CS XP:     {data.get('xp_computacao', 0)}\n"
        f"  Progresso: {barra}\n"
        f"  Próximo:   {xp_proximo}\n"
        f"{'─' * 44}\n"
        f"  {streak_emoji} Streak atual:  {streak} dia(s)\n"
        f"  Streak máximo: {data.get('streak_maximo', 0)} dia(s)\n"
        f"  Multiplicador: {mult_str}\n"
        f"{'─' * 44}\n"
        f"  Últimas atividades:\n{hist_str}\n"
        f"{'═' * 44}\n"
    )