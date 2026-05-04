"""
Testes unitários para tools/ingles_tool.py

Cobertura:
- registrar_sessao_ingles: happy path, tipo inválido, duração
- consultar_progresso_ingles: vazio, com sessões, breakdown por tipo
- adicionar_vocabulario: happy path, duplicata
- revisar_vocabulario: vazio, com palavras, filtro por categoria
- sugerir_conteudo_ingles: temas conhecidos e desconhecidos
- gerar_prompt_escrita: tipos válidos
"""

import json
import pytest
from tools.ingles_tool import (
    registrar_sessao_ingles,
    consultar_progresso_ingles,
    adicionar_vocabulario,
    revisar_vocabulario,
    sugerir_conteudo_ingles,
    gerar_prompt_escrita,
)


# ── registrar_sessao_ingles ───────────────────────────────────────────────

class TestRegistrarSessaoIngles:

    def test_registra_com_sucesso(self, tmp_storage_ingles):
        result = registrar_sessao_ingles.invoke({
            "tipo": "podcast",
            "descricao": "Ouvi Syntax.fm por 30 min",
            "duracao_minutos": 30,
            "observacoes": "",
        })
        assert "✅" in result
        assert "podcast" in result

    def test_acumula_tempo_total(self, tmp_storage_ingles):
        registrar_sessao_ingles.invoke({
            "tipo": "escrita",
            "descricao": "Escrevi email formal",
            "duracao_minutos": 20,
            "observacoes": "",
        })
        registrar_sessao_ingles.invoke({
            "tipo": "youtube",
            "descricao": "Assisti Fireship",
            "duracao_minutos": 15,
            "observacoes": "",
        })
        result = consultar_progresso_ingles.invoke({})
        assert "35" in result or "0h 35min" in result

    def test_valida_tipo_invalido(self, tmp_storage_ingles):
        result = registrar_sessao_ingles.invoke({
            "tipo": "gaming",  # inválido
            "descricao": "Joguei em inglês",
            "duracao_minutos": 60,
            "observacoes": "",
        })
        assert "validação" in result.lower()

    def test_valida_duracao_zero(self, tmp_storage_ingles):
        result = registrar_sessao_ingles.invoke({
            "tipo": "leitura",
            "descricao": "Li artigo",
            "duracao_minutos": 0,
            "observacoes": "",
        })
        assert "validação" in result.lower()


# ── consultar_progresso_ingles ────────────────────────────────────────────

class TestConsultarProgressoIngles:

    def test_retorna_mensagem_quando_vazio(self, tmp_storage_ingles):
        result = consultar_progresso_ingles.invoke({})
        assert "no sessions" in result.lower() or "nenhuma" in result.lower()

    def test_mostra_breakdown_por_tipo(self, tmp_storage_ingles):
        registrar_sessao_ingles.invoke({
            "tipo": "escrita",
            "descricao": "Escrevi essay",
            "duracao_minutos": 45,
            "observacoes": "",
        })
        result = consultar_progresso_ingles.invoke({})
        assert "escrita" in result
        assert "📊" in result


# ── adicionar_vocabulario ─────────────────────────────────────────────────

class TestAdicionarVocabulario:

    def test_adiciona_palavra_com_sucesso(self, tmp_storage_ingles):
        result = adicionar_vocabulario.invoke({
            "palavra": "throughput",
            "traducao": "vazão, capacidade de processamento",
            "exemplo": "The system throughput increased after optimization.",
            "categoria": "tech",
        })
        assert "✅" in result
        assert "throughput" in result

    def test_rejeita_duplicata(self, tmp_storage_ingles):
        adicionar_vocabulario.invoke({
            "palavra": "latency",
            "traducao": "latência",
            "exemplo": "High latency affects user experience.",
            "categoria": "tech",
        })
        result = adicionar_vocabulario.invoke({
            "palavra": "latency",
            "traducao": "latência",
            "exemplo": "High latency affects user experience.",
            "categoria": "tech",
        })
        assert "already in" in result.lower()

    def test_persiste_no_storage(self, tmp_storage_ingles):
        adicionar_vocabulario.invoke({
            "palavra": "resilience",
            "traducao": "resiliência",
            "exemplo": "System resilience is key in distributed architectures.",
            "categoria": "tech",
        })
        with open(tmp_storage_ingles, "r") as f:
            data = json.load(f)
        assert len(data["vocabulario"]) == 1
        assert data["vocabulario"][0]["palavra"] == "resilience"


# ── revisar_vocabulario ───────────────────────────────────────────────────

class TestRevisarVocabulario:

    def test_retorna_mensagem_quando_vazio(self, tmp_storage_ingles):
        result = revisar_vocabulario.invoke({"categoria": "", "quantidade": 5})
        assert "empty" in result.lower() or "vazio" in result.lower()

    def test_retorna_palavras_salvas(self, tmp_storage_ingles):
        adicionar_vocabulario.invoke({
            "palavra": "idempotent",
            "traducao": "idempotente",
            "exemplo": "REST DELETE is idempotent.",
            "categoria": "tech",
        })
        result = revisar_vocabulario.invoke({"categoria": "", "quantidade": 5})
        assert "idempotent" in result

    def test_filtra_por_categoria(self, tmp_storage_ingles):
        adicionar_vocabulario.invoke({
            "palavra": "nevertheless",
            "traducao": "no entanto",
            "exemplo": "Nevertheless, the system remained stable.",
            "categoria": "daily",
        })
        adicionar_vocabulario.invoke({
            "palavra": "microservice",
            "traducao": "microsserviço",
            "exemplo": "Each microservice handles one responsibility.",
            "categoria": "tech",
        })
        result = revisar_vocabulario.invoke({"categoria": "daily", "quantidade": 5})
        assert "nevertheless" in result
        assert "microservice" not in result


# ── sugerir_conteudo_ingles ───────────────────────────────────────────────

class TestSugerirConteudo:

    def test_sugere_conteudo_tech(self, tmp_storage_ingles):
        result = sugerir_conteudo_ingles.invoke({"tema": "tech", "nivel": "intermediate"})
        assert "YouTube" in result or "Podcast" in result
        assert "Fireship" in result or "Syntax" in result

    def test_sugere_conteudo_ai(self, tmp_storage_ingles):
        result = sugerir_conteudo_ingles.invoke({"tema": "AI", "nivel": "advanced"})
        assert "Karpathy" in result or "Lex Fridman" in result

    def test_fallback_para_tech_quando_tema_desconhecido(self, tmp_storage_ingles):
        result = sugerir_conteudo_ingles.invoke({"tema": "cooking", "nivel": "intermediate"})
        assert "YouTube" in result  # fallback funciona

    def test_contem_dica_de_consistencia(self, tmp_storage_ingles):
        result = sugerir_conteudo_ingles.invoke({"tema": "", "nivel": "intermediate"})
        assert "consistency" in result.lower() or "daily" in result.lower()


# ── gerar_prompt_escrita ──────────────────────────────────────────────────

class TestGerarPromptEscrita:

    def test_gera_prompt_email(self, tmp_storage_ingles):
        result = gerar_prompt_escrita.invoke({"tipo": "email", "contexto": ""})
        assert "Email" in result
        assert "150" in result or "200" in result

    def test_gera_prompt_linkedin(self, tmp_storage_ingles):
        result = gerar_prompt_escrita.invoke({"tipo": "linkedin", "contexto": ""})
        assert "LinkedIn" in result
        assert "hook" in result.lower()

    def test_gera_prompt_essay(self, tmp_storage_ingles):
        result = gerar_prompt_escrita.invoke({"tipo": "essay", "contexto": "AI in healthcare"})
        assert "AI in healthcare" in result

    def test_contexto_personalizado(self, tmp_storage_ingles):
        result = gerar_prompt_escrita.invoke({
            "tipo": "email",
            "contexto": "requesting a day off for a conference",
        })
        assert "requesting a day off" in result