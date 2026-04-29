import json
import os
from datetime import datetime
from langchain_core.tools import tool

STORAGE_FILE = "storage/ingles.json"

# ── Helpers ────────────────────────────────────────────────────────────────

def _load() -> dict:
    if not os.path.exists(STORAGE_FILE):
        return {"sessoes": [], "exercicios": [], "vocabulario": []}
    with open(STORAGE_FILE, "r", encoding="utf-8") as f:
        content = f.read().strip()
        if not content:
            return {"sessoes": [], "exercicios": [], "vocabulario": []}
        return json.loads(content)

def _save(data: dict):
    os.makedirs("storage", exist_ok=True)
    with open(STORAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ── Tool 1: registrar sessão de estudo ────────────────────────────────────

@tool
def registrar_sessao_ingles(
    tipo:str,
    descricao:str,
    duracao_minutos:int,
    observacoes:str="",
) -> str:
    """
    Registra uma sessão de estudo de inglês (escrita, leitura, podcast, YouTube, etc).
    Use quando o usuário informar que praticou inglês de qualquer forma.
 
    Args:
        tipo: Tipo de prática. Valores: 'escrita', 'fala', 'podcast', 'youtube', 'vocabulario', 'leitura'.
        descricao: O que foi praticado. Exemplo: 'Escrevi email formal para cliente'.
        duracao_minutos: Duração da sessão em minutos.
        observacoes: Dificuldades encontradas ou palavras novas aprendidas.
 
    Returns:
        Confirmação do registro com estatísticas acumuladas.
    """
    data = _load()

    sessao = {
        "tipo": tipo,
        "descricao": descricao,
        "duracao_minutos": duracao_minutos,
        "observacoes": observacoes,
        "data": datetime.now().strftime("%Y-%m-%d"),
        "hora": datetime.now().strftime("%H:%M"),
    }

    data["sessoes"].append(sessao)
    _save(data)

    total_min = sum(s["duracao_minutos"] for s in data["sessoes"])
    total_h = total_min // 60
    total_m = total_min % 60

    return (
        f"✅ Session registered: {tipo} — {duracao_minutos} min\n"
        f"Total study time: {total_h}h {total_m}min across {len(data['sessoes'])} sessions."
    )

# ── Tool 2: consultar progresso de inglês ─────────────────────────────────

@tool
def consultar_progresso_ingles() -> str:
    """
    Retorna o progresso de estudos de inglês: total de horas, breakdown por tipo
    e consistência semanal.
    Use quando o usuário perguntar sobre seu progresso em inglês.
 
    Returns:
        Resumo completo do progresso.
    """
    data = _load()
    sessoes = data.get("sessoes", [])

    if not sessoes:
        return "No sessions registered yet. Start practicing and I'll track your progress!"
    
    total_min = sum(s["duracao_minutos"] for s in sessoes)
    total_h = total_min // 60
    total_m = total_min % 60

    por_tipo: dict = {}
    for s in sessoes:
        t = s["tipo"]
        por_tipo[t] = por_tipo.get(t, 0) + s["duracao_minutos"]

        tipo_str = "\n".join(
            f"  • {t}: {v // 60}h {v % 60}min" for t, v in sorted(por_tipo.items())
        )

        # sessoes nos ultimos 7 dias
        hoje = datetime.now().data()
        recentes = [
            s for s in sessoes
            if (hoje - datetime.strptime(s["data"], "%Y-%m-%d").date()).days <= 7
        ]

        return (
            f"📊 English Study Progress\n\n"
            f"Total time: {total_h}h {total_m}min — {len(sessoes)} sessions\n\n"
            f"By type:\n{tipo_str}\n\n"
            f"Last 7 days: {len(recentes)} sessions — "
            f"{sum(s['duracao_minutos'] for s in recentes)} min"
        )
    
# ── Tool 3: registrar palavra/expressão no vocabulário ───────────────────

@tool
def adicionar_vocabulario(
    palavra: str,
    traducao: str,
    exemplo: str,
    categoria: str = "geral",
) -> str:
    """
    Adiciona uma palavra ou expressão ao vocabulário pessoal do usuário.
    Use quando o usuário aprender uma palavra nova ou pedir para salvar uma expressão.
 
    Args:
        palavra: Palavra ou expressão em inglês.
        traducao: Tradução ou explicação em português.
        exemplo: Exemplo de uso em uma frase em inglês.
        categoria: Categoria. Exemplos: 'tech', 'business', 'daily', 'phrasal verbs', 'geral'.
 
    Returns:
        Confirmação com total de palavras no vocabulário.
    """
    data = _load()

    # evita duplicata
    existente = next(
        (v for v in data["vocabulario"] if v["palavra"].lower() == palavra.lower()), None
    )
    if existente:
        return f"'{palavra}' is already in your vocabulary list."
    
    entry = {
        "palavra": palavra,
        "traducao": traducao,
        "exemplo": exemplo,
        "categoria": categoria,
        "adicionado_em": datetime.now().strftime("%Y-%m-%d"),
    }

    data["vocabulario"].append(entry)
    _save(data)

    total = len(data["vocabulario"])
    return (
        f"✅ '{palavra}' added to your vocabulary!\n"
        f"Example: {exemplo}\n"
        f"Total words saved: {total}"
    )

# ── Tool 4: revisar vocabulário ───────────────────────────────────────────

@tool
def revisar_vocabulario(categoria: str = "", quantidade: int = 5) -> str:
    """
    Retorna palavras do vocabulário pessoal para revisão.
    Use quando o usuário quiser revisar palavras aprendidas.
 
    Args:
        categoria: Filtra por categoria. Deixe vazio para todas.
        quantidade: Número de palavras para revisar. Padrão: 5.
 
    Returns:
        Lista de palavras com tradução e exemplo para revisão.
    """
    data = _load()
    vocab = data.get("vocabulario", [])

    if not vocab:
        return "Your vocabulary list is empty. Start adding words as you learn them!"
    
    if categoria:
        vocab = [v for v in vocab if v["categoria"].lower() == categoria.lower()]
        if not vocab:
            return f"No words found in category '{categoria}'."
        
    # pega as mais recentes
    selecionadas = vocab[-quantidade:]

    linhas = [f"📚 Vocabulary Review — {len(selecionadas)} words\n"]
    for v in selecionadas:
        linhas.append(
            f"🔹 {v['palavra']} [{v['categoria']}]\n"
            f"   → {v['traducao']}\n"
            f"   Example: {v['exemplo']}"
        )

    return "\n\n".join(linhas)

# ── Tool 5: sugerir conteúdos de input ───────────────────────────────────

@tool
def sugerir_conteudo_ingles(tema: str = "", nivel: str = "intermediate") -> str:
    """
    Sugere conteúdos de input em inglês: YouTube channels, podcasts e recursos.
    Use quando o usuário pedir sugestões de conteúdo para ouvir ou assistir.
 
    Args:
        tema: Tema de interesse. Exemplos: 'tech', 'AI', 'business', 'daily conversation', 'news'.
        nivel: Nível do inglês. Valores: 'beginner', 'intermediate', 'advanced'. Padrão: 'intermediate'.
 
    Returns:
        Lista curada de sugestões com links e descrições.
    """
    sugestoes = {
        "tech": {
            "youtube": [
                ("Fireship", "https://youtube.com/@Fireship", "Fast-paced tech explanations, great for listening"),
                ("Theo — t3.gg", "https://youtube.com/@t3dotgg", "Web dev discussions, natural English"),
                ("ThePrimeagen", "https://youtube.com/@ThePrimeagen", "Dev culture, fast natural speech"),
            ],
            "podcast": [
                ("Syntax.fm", "https://syntax.fm", "Web development, intermediate level"),
                ("The Changelog", "https://changelog.com/podcast", "Open source & tech industry"),
                ("Software Engineering Daily", "https://softwareengineeringdaily.com", "Deep technical topics"),
            ],
        },
        "AI": {
            "youtube": [
                ("Andrej Karpathy", "https://youtube.com/@AndrejKarpathy", "Deep learning explained clearly"),
                ("Yannic Kilcher", "https://youtube.com/@YannicKilcher", "ML paper walkthroughs"),
                ("AI Explained", "https://youtube.com/@aiexplained-official", "AI news and trends"),
            ],
            "podcast": [
                ("Lex Fridman Podcast", "https://lexfridman.com/podcast", "Long-form AI and tech interviews"),
                ("TWIML AI Podcast", "https://twimlai.com", "ML research and applications"),
            ],
        },
        "business": {
            "youtube": [
                ("Harvard Business Review", "https://youtube.com/@HarvardBusinessReview", "Business English, formal register"),
                ("Simon Sinek", "https://youtube.com/@SimonSinek", "Leadership and communication"),
            ],
            "podcast": [
                ("How I Built This", "https://npr.org/series/how-i-built-this", "Startup stories, narrative English"),
                ("Masters of Scale", "https://mastersofscale.com", "Business growth, natural conversational English"),
            ],
        },
        "daily": {
            "youtube": [
                ("English with Lucy", "https://youtube.com/@EnglishwithLucy", "Pronunciation and daily expressions"),
                ("Rachel's English", "https://youtube.com/@rachelsenglish", "American accent training"),
            ],
            "podcast": [
                ("6 Minute English (BBC)", "https://bbc.co.uk/learningenglish/english/features/6-minute-english", "Short episodes, great for beginners/intermediate"),
                ("All Ears English", "https://allearsenglish.com", "Natural American English conversations"),
            ],
        },
    }
 
    # fallback para tech se tema não encontrado
    tema_key = tema.lower() if tema.lower() in sugestoes else "tech"
    conteudo = sugestoes[tema_key]
 
    linhas = [f"🎯 Content suggestions for: {tema or 'tech'} ({nivel})\n"]
 
    linhas.append("📺 YouTube:")
    for nome, link, desc in conteudo["youtube"]:
        linhas.append(f"  • {nome}\n    {link}\n    → {desc}")
 
    linhas.append("\n🎙️ Podcasts:")
    for nome, link, desc in conteudo["podcast"]:
        linhas.append(f"  • {nome}\n    {link}\n    → {desc}")
 
    linhas.append(
        f"\n💡 Tip: Watch/listen for 20-30 min daily. "
        f"Don't worry about understanding 100% — consistency beats perfection."
    )
 
    return "\n".join(linhas)
 
# ── Tool 6: gerar exercício de escrita ───────────────────────────────────

@tool
def gerar_prompt_escrita(tipo: str = "email", contexto: str = "") -> str:
    """
    Gera um prompt de exercício de escrita em inglês para o usuário praticar.
    Use quando o usuário pedir um exercício de escrita ou quiser praticar.
 
    Args:
        tipo: Tipo de escrita. Valores: 'email', 'essay', 'summary', 'dialogue', 'linkedin'.
        contexto: Contexto ou tema específico desejado. Exemplo: 'tech job application', 'AI ethics'.
 
    Returns:
        Prompt de exercício com instruções claras.
    """
    prompts = {
        "email": (
            f"✍️ Writing Exercise — Professional Email\n\n"
            f"Scenario: {contexto or 'You are a software developer writing to your team lead about a project delay caused by an unexpected technical issue.'}\n\n"
            f"Write a professional email (150-200 words) that:\n"
            f"  • Has a clear subject line\n"
            f"  • Explains the situation objectively\n"
            f"  • Proposes a solution or next steps\n"
            f"  • Uses a formal but friendly tone\n\n"
            f"When you're done, share your text and I'll give you detailed feedback."
        ),
        "essay": (
            f"✍️ Writing Exercise — Short Essay\n\n"
            f"Topic: {contexto or 'How is Artificial Intelligence changing the software development industry?'}\n\n"
            f"Write a short essay (200-250 words) with:\n"
            f"  • An introduction with a clear thesis\n"
            f"  • 2 body paragraphs with examples\n"
            f"  • A conclusion\n\n"
            f"Share your essay when ready for feedback."
        ),
        "summary": (
            f"✍️ Writing Exercise — Summary\n\n"
            f"Task: {contexto or 'Summarize the concept of RAG (Retrieval-Augmented Generation) for a non-technical manager.'}\n\n"
            f"Write a clear summary (100-150 words) that:\n"
            f"  • Avoids jargon or explains it simply\n"
            f"  • Focuses on the business value\n"
            f"  • Is easy to understand for a non-developer\n\n"
            f"Share your text for feedback."
        ),
        "linkedin": (
            f"✍️ Writing Exercise — LinkedIn Post\n\n"
            f"Topic: {contexto or 'Share something you learned recently about AI agents.'}\n\n"
            f"Write a LinkedIn post (100-150 words) that:\n"
            f"  • Starts with a hook (first line must grab attention)\n"
            f"  • Shares a genuine insight or lesson\n"
            f"  • Ends with a question to engage the audience\n"
            f"  • Uses short paragraphs (LinkedIn style)\n\n"
            f"Share your post when ready."
        ),
        "dialogue": (
            f"✍️ Writing Exercise — Dialogue\n\n"
            f"Scenario: {contexto or 'A job interview at a tech company where you are asked about your experience with machine learning.'}\n\n"
            f"Write a realistic dialogue (10-15 exchanges) between:\n"
            f"  • Interviewer (technical questions)\n"
            f"  • You (confident, specific answers with examples)\n\n"
            f"Share the dialogue for feedback."
        ),
    }

    return prompts.get(tipo, prompts["email"])