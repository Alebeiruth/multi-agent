"""
Testes unitários para tools/estatistica_tool.py

Cobertura:
- registrar_aula: happy path, duplicata, validação Pydantic
- consultar_progresso_estatistica: vazio, com dados
- calcular_revisoes: datas corretas (D+0, D+3, D+5)
- marcar_revisao_feita: happy path, revisão duplicada, inválida
- gerar_conteudo_email_revisao: estrutura do email
"""

import json

import pytest

from tools.estatistica_tool import (
    calcular_revisoes,
    consultar_progresso_estatistica,
    gerar_conteudo_email_revisao,
    marcar_revisao_feita,
    registrar_aula,
)

# ── registrar_aula ─────────────────────────────────────────────────────────


class TestRegistrarAula:
    def test_registra_aula_com_sucesso(self, tmp_storage_estatistica):
        result = registrar_aula.invoke(
            {
                "numero": 1,
                "tema": "Distribuição Normal",
                "conteudos": "média, variância, desvio padrão",
                "data_aula": "2026-05-07",
                "observacoes": "",
            }
        )
        assert "✅" in result
        assert "Distribuição Normal" in result

    def test_aula_registrada_persiste_no_storage(self, tmp_storage_estatistica):
        registrar_aula.invoke(
            {
                "numero": 2,
                "tema": "Teste de Hipóteses",
                "conteudos": "p-valor, hipótese nula",
                "data_aula": "2026-05-14",
                "observacoes": "",
            }
        )
        with open(tmp_storage_estatistica) as f:
            data = json.load(f)
        assert len(data["aulas"]) == 1
        assert data["aulas"][0]["tema"] == "Teste de Hipóteses"

    def test_rejeita_duplicata(self, aula_registrada):
        result = registrar_aula.invoke(
            {
                "numero": 1,
                "tema": "Outra coisa",
                "conteudos": "conteudo qualquer",
                "data_aula": "2026-05-07",
                "observacoes": "",
            }
        )
        assert "já registrada" in result

    def test_usa_data_atual_quando_vazio(self, tmp_storage_estatistica):
        result = registrar_aula.invoke(
            {
                "numero": 3,
                "tema": "Regressão Linear",
                "conteudos": "coeficientes, R²",
                "data_aula": "",
                "observacoes": "",
            }
        )
        assert "✅" in result

    def test_valida_numero_aula_invalido(self, tmp_storage_estatistica):
        result = registrar_aula.invoke(
            {
                "numero": 9,  # máximo é 8
                "tema": "Tema",
                "conteudos": "conteudo",
                "data_aula": "",
                "observacoes": "",
            }
        )
        assert "validação" in result.lower()

    def test_valida_data_formato_errado(self, tmp_storage_estatistica):
        result = registrar_aula.invoke(
            {
                "numero": 4,
                "tema": "Tema",
                "conteudos": "conteudo",
                "data_aula": "07/05/2026",  # formato errado
                "observacoes": "",
            }
        )
        assert "validação" in result.lower()

    def test_calcula_revisoes_no_registro(self, tmp_storage_estatistica):
        result = registrar_aula.invoke(
            {
                "numero": 1,
                "tema": "Distribuição Normal",
                "conteudos": "média, variância",
                "data_aula": "2026-05-07",
                "observacoes": "",
            }
        )
        assert "Revisão 1" in result
        assert "Revisão 2" in result
        assert "Revisão 3" in result


# ── consultar_progresso_estatistica ───────────────────────────────────────


class TestConsultarProgresso:
    def test_retorna_mensagem_quando_vazio(self, tmp_storage_estatistica):
        result = consultar_progresso_estatistica.invoke({})
        assert (
            "nenhuma" in result.lower()
            or "cadastrada" in result.lower()
            or "registrada" in result.lower()
        )

    def test_mostra_progresso_com_aula(self, aula_registrada):
        result = consultar_progresso_estatistica.invoke({})
        assert "1/8" in result or "Distribuição Normal" in result

    def test_mostra_aulas_pendentes(self, aula_registrada):
        result = consultar_progresso_estatistica.invoke({})
        assert "pendentes" in result.lower() or "2" in result


# ── calcular_revisoes ─────────────────────────────────────────────────────


class TestCalcularRevisoes:
    def test_retorna_tres_datas(self, aula_registrada):
        result = calcular_revisoes.invoke({"numero_aula": 1})
        assert "Revisão 1" in result
        assert "Revisão 2" in result
        assert "Revisão 3" in result

    def test_datas_corretas_d0_d3_d5(self, aula_registrada):
        """Aula em 2026-05-07 (quarta) → revisões em 07, 10 e 12."""
        result = calcular_revisoes.invoke({"numero_aula": 1})
        assert "2026-05-07" in result  # D+0 quarta
        assert "2026-05-10" in result  # D+3 sábado
        assert "2026-05-12" in result  # D+5 segunda

    def test_aula_nao_encontrada(self, tmp_storage_estatistica):
        result = calcular_revisoes.invoke({"numero_aula": 5})
        assert "não encontrada" in result


# ── marcar_revisao_feita ──────────────────────────────────────────────────


class TestMarcarRevisaoFeita:
    def test_marca_revisao_com_sucesso(self, aula_registrada):
        result = marcar_revisao_feita.invoke(
            {
                "numero_aula": 1,
                "numero_revisao": 1,
            }
        )
        assert "✅" in result
        assert "1/3" in result

    def test_nao_duplica_revisao(self, aula_registrada):
        marcar_revisao_feita.invoke({"numero_aula": 1, "numero_revisao": 1})
        result = marcar_revisao_feita.invoke({"numero_aula": 1, "numero_revisao": 1})
        assert "já estava marcada" in result

    def test_valida_revisao_invalida(self, aula_registrada):
        result = marcar_revisao_feita.invoke(
            {
                "numero_aula": 1,
                "numero_revisao": 5,  # só existe 1, 2, 3
            }
        )
        assert "validação" in result.lower()

    def test_aula_nao_encontrada(self, tmp_storage_estatistica):
        result = marcar_revisao_feita.invoke(
            {
                "numero_aula": 7,
                "numero_revisao": 1,
            }
        )
        assert "não encontrada" in result


# ── gerar_conteudo_email_revisao ──────────────────────────────────────────


class TestGerarEmailRevisao:
    def test_email_contem_campos_obrigatorios(self, aula_registrada):
        result = gerar_conteudo_email_revisao.invoke(
            {
                "numero_aula": 1,
                "numero_revisao": 1,
            }
        )
        data = json.loads(result)
        assert "destinatario" in data
        assert "assunto" in data
        assert "corpo" in data

    def test_assunto_contem_tema(self, aula_registrada):
        result = gerar_conteudo_email_revisao.invoke(
            {
                "numero_aula": 1,
                "numero_revisao": 2,
            }
        )
        data = json.loads(result)
        assert "Distribuição Normal" in data["assunto"]

    def test_aula_nao_encontrada(self, tmp_storage_estatistica):
        result = gerar_conteudo_email_revisao.invoke(
            {
                "numero_aula": 8,
                "numero_revisao": 1,
            }
        )
        assert "não encontrada" in result
