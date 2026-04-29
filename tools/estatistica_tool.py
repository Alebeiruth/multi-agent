import json
import os
from datetime import datetime, timedelta
from langchain_core.tools import tool

STORAGE_FILE = "storage/estatistica.json"
TOTAL_AULAS = 8
EMAIL_ALEXANDRE = os.getenv("ALEXANDRE_EMAIL", "alexandrebeyruth@gmail.com")

# ── Helpers ────────────────────────────────────────────────────────────────

def _load() -> dict:
    if not os.path.exists(STORAGE_FILE):
        return {"aulas": [], "total_aulas": TOTAL_AULAS}
    with open(STORAGE_FILE, "r", encoding="utf-8") as f:
        content = f.read().strip()
        if not content:
            return {"aulas":[], "total_aulas": TOTAL_AULAS}
        return json.loads(content)

def _save(data: dict):
    os.makedirs("storage", exist_ok=True)
    with open(STORAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def _proximas_revisoes(data_aula: str) -> dict:
    """
    Calcula as 3 datas de revisão a partir da data da aula.
    Aulas são às quartas → revisões na quarta (D+0), sábado (D+3) e segunda (D+5).
    Retorna dict com as datas no formato 'YYYY-MM-DD HH:MM'.
    """
    base = datetime.strptime(data_aula, "%Y-%m-%d")
    return {
        "revisao_1": (base).strftime("%Y-%m-%d 20:00"),           # quarta mesmo dia
        "revisao_2": (base + timedelta(days=3)).strftime("%Y-%m-%d 20:00"),  # sábado
        "revisao_3": (base + timedelta(days=5)).strftime("%Y-%m-%d 20:00"),  # segunda
    }

# ── Tool 1: registrar aula ─────────────────────────────────────────────────

@tool
def registrar_aula(
    numero: int,
    tema: str,
    conteudos: str,
    data_aula: str = "",
    observacoes: str = "",
) -> str:
    """
    Registra uma aula de Estatística e Probabilidade assistida.
    Use SEMPRE que o usuário informar que assistiu ou concluiu uma aula.
 
    Args:
        numero: Número da aula (1 a 8).
        tema: Tema principal da aula. Exemplo: 'Distribuição Normal', 'Teste de Hipóteses'.
        conteudos: Conteúdos abordados na aula, separados por vírgula.
        data_aula: Data da aula no formato 'YYYY-MM-DD'. Deixe vazio para usar hoje.
        observacoes: Dúvidas ou pontos de atenção para revisão.
 
    Returns:
        Confirmação do registro com as datas de revisão calculadas.
    """
    data = _load()

    # verifica duplicata
    existente = next((a for a in data["aulas"] if a ["numero"] == numero), None)
    if existente:
        return (
            f"Aula {numero} já registrada em {existente['data_aula']}. "
            f"Use atualizar_aula para modificar.)"
        )

    if not data_aula:
        data_aula = datetime.now().strftime("%Y-%m-%d")

        revisoes = _proximas_revisoes(data_aula)

        nova_aula = {
            "numero": numero,
        "tema": tema,
        "conteudos": conteudos,
        "data_aula": data_aula,
        "observacoes": observacoes,
        "revisoes": revisoes,
        "revisoes_feitas": [],
        "registrado_em": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }

        data["aulas"].append(nova_aula)
        data["aulas"].sort(key=lambda x: x["numero"])
        _save(data)

        return (
        f"✅ Aula {numero} — '{tema}' registrada.\n\n"
        f"📅 Revisões agendadas:\n"
        f"  • Revisão 1 (quarta): {revisoes['revisao_1']}\n"
        f"  • Revisão 2 (sábado): {revisoes['revisao_2']}\n"
        f"  • Revisão 3 (segunda): {revisoes['revisao_3']}\n\n"
        f"Agora use agendar_revisoes_calendario e enviar_emails_revisao para completar o agendamento."
    )

# ── Tool 2: consultar progresso da matéria ────────────────────────────────

@tool
def consultar_progresso_estatistica() -> str:
    """
    Retorna o progresso atual na matéria de Estatística e Probabilidade.
    Mostra aulas assistidas, temas cobertos e aulas restantes.
    Use quando o usuário perguntar sobre progresso ou quantas aulas faltam.
 
    Returns:
        Resumo do progresso com aulas concluídas e pendentes.
    """
    data = _load()
    aulas = data.get("aulas", [])
    total = data.get("total_aulas", TOTAL_AULAS)
    concluidas = len(aulas)
    restantes = total - concluidas

    if not aulas:
        return (
            f"Nenhuma aula registrada ainda.\n"
            f"Total da matéria: {total} aulas."
        )
    
    linhas = [f"📊 Estatística e Probabilidade — Progresso\n"]
    linhas.append(f"Concluídas: {concluidas}/{total} aulas | Restantes: {restantes}\n")

    for aula in aulas:
        revisoes_feitas = len(aula.get("revisoes_feitas", []))
        linhas.append(
            f"  ✅ Aula {aula['numero']}: {aula['tema']} "
            f"({aula['data_aula']}) — {revisoes_feitas}/3 revisões"
        )

        numeros_feitos = {a["numero"] for a in aulas}
        pendentes = [i for i in range(1, total +1) if i not in numeros_feitos]
        if pendentes:
            linhas.append(f"\nAulas pendentes: {', '.join(str(p) for p in pendentes)}")
 
    return "\n".join(linhas)

# ── Tool 3: calcular datas de revisão ─────────────────────────────────────

@tool
def calcular_revisoes(numero_aula: int) -> str:
    """
    Retorna as datas de revisão de uma aula específica.
    Use antes de agendar no calendário ou enviar emails.
 
    Args:
        numero_aula: Número da aula registrada.
 
    Returns:
        Datas das 3 revisões no formato 'YYYY-MM-DD HH:MM'.
    """
    data = _load()
    aula = next((a for a in data["aulas"] if a["numero"] == numero_aula), None)

    if not aula:
        return f"Aula {numero_aula} não encontrada. Registre-a primeiro com registrar_aula."
    
    revisoes = aula["revisoes"]
    return (
        f"📅 Revisões da Aula {numero_aula} — {aula['tema']}:\n"
        f"  • Revisão 1 (quarta): {revisoes['revisao_1']}\n"
        f"  • Revisão 2 (sábado): {revisoes['revisao_2']}\n"
        f"  • Revisão 3 (segunda): {revisoes['revisao_3']}"
    )
 

 # ── Tool 4: marcar revisão como feita ────────────────────────────────────

@tool
def marcar_revisao_feita(numero_aula: int, numero_revisao: int) -> str:
    """
    Marca uma das 3 revisões de uma aula como concluída.
 
    Args:
        numero_aula: Número da aula (1 a 8).
        numero_revisao: Número da revisão concluída (1, 2 ou 3).
 
    Returns:
        Confirmação com progresso de revisões da aula.
    """
    data = _load()
    aula = next((a for a in data["aulas"] if a["numero"] == numero_aula), None)

    if not aula:
        return f"Aula {numero_aula} não encontrada"
    
    chave = f"revisao_{numero_revisao}"
    if chave not in aula["revisoes"]:
        return f"Revisão {numero_revisao} inválida. Use 1, 2 ou 3."
    
    feitas = aula.setdefault("reviseos_feitas", [])
    if numero_revisao in feitas:
        return f"Revisão {numero_revisao} da aula {numero_aula} já estava marcada."
    
    feitas.append(numero_revisao)
    _save(data)
 
    total_feitas = len(feitas)
    return (
        f"✅ Revisão {numero_revisao} da Aula {numero_aula} ({aula['tema']}) concluída.\n"
        f"Progresso de revisões: {total_feitas}/3"
    )


# ── Tool 5: gerar corpo do email de revisão ──────────────────────────────

@tool
def gerar_conteudo_email_revisao(numero_aula: int, numero_revisao: int) -> str:
    """
    Gera o assunto e corpo do email de lembrete de revisão para uma aula.
    Use esta tool para obter o conteúdo antes de enviar via Gmail MCP.
 
    Args:
        numero_aula: Número da aula (1 a 8).
        numero_revisao: Número da revisão (1, 2 ou 3).
 
    Returns:
        Dict serializado com 'destinatario', 'assunto' e 'corpo' do email.
    """
    data = _load()
    aula = next((a for a in data["aulas"] if a["numero"] == numero_aula), None)

    if not aula:
        return f"Aula {numero_aula} não encontrada."
 
    labels = {1: "1ª revisão — mesmo dia", 2: "2ª revisão — 3 dias depois", 3: "3ª revisão — 5 dias depois"}
    label = labels.get(numero_revisao, f"Revisão {numero_revisao}")
 
    assunto = f"📐 Revisão Estatística: {aula['tema']} ({label})"
 
    corpo = f"""Olá Alexandre!
 
Este é o seu lembrete de revisão de Estatística e Probabilidade.
 
📚 Aula {aula['numero']}: {aula['tema']}
📅 Aula assistida em: {aula['data_aula']}
🔁 {label}
 
Conteúdos para revisar:
{aula['conteudos']}
"""
 
    if aula.get("observacoes"):
        corpo += f"\n⚠️ Pontos de atenção:\n{aula['observacoes']}\n"
 
    corpo += """
Dicas para a revisão:
• Releia suas anotações dos pontos principais
• Resolva 2-3 exercícios sobre o tema
• Se tiver dúvidas, pergunte ao agente de Estatística
 
Bons estudos! 🎓
"""
 
    resultado = {
        "destinatario": EMAIL_ALEXANDRE,
        "assunto": assunto,
        "corpo": corpo,
    }
 
    return json.dumps(resultado, ensure_ascii=False, indent=2)









 







    
