"""
Testes unitários para tools/validators.py

Garante que cada modelo Pydantic aceita inputs válidos
e rejeita inputs inválidos com mensagens claras.
"""

from pydantic import ValidationError
import pytest

from tools.validators import (
    AdicionarVocabularioInput,
    AgendarSessaoInput,
    RegistrarAulaInput,
    RegistrarDuvidaCursoInput,
    RegistrarEstudoCSInput,
    RegistrarModuloAWSInput,
    RegistrarModuloDCInput,
    RegistrarSessaoInglesInput,
    RegistrarXPAWSInput,
    RegistrarXPCSInput,
    RevisaoInput,
)

# ── RegistrarAulaInput ─────────────────────────────────────────────────────


class TestRegistrarAulaInput:
    def test_valido(self):
        obj = RegistrarAulaInput(numero=1, tema="Distribuição Normal", conteudos="média, variância")
        assert obj.numero == 1

    def test_numero_abaixo_do_minimo(self):
        with pytest.raises(ValidationError):
            RegistrarAulaInput(numero=0, tema="Tema", conteudos="x")

    def test_numero_acima_do_maximo(self):
        with pytest.raises(ValidationError):
            RegistrarAulaInput(numero=9, tema="Tema", conteudos="x")

    def test_tema_vazio(self):
        with pytest.raises(ValidationError):
            RegistrarAulaInput(numero=1, tema="", conteudos="x")

    def test_data_formato_invalido(self):
        with pytest.raises(ValidationError):
            RegistrarAulaInput(numero=1, tema="Tema", conteudos="x", data_aula="07/05/2026")

    def test_data_formato_valido(self):
        obj = RegistrarAulaInput(numero=1, tema="Tema", conteudos="xyz", data_aula="2026-05-07")
        assert obj.data_aula == "2026-05-07"

    def test_data_vazia_e_valida(self):
        obj = RegistrarAulaInput(numero=1, tema="Tema", conteudos="xyz", data_aula="")
        assert obj.data_aula == ""


# ── RevisaoInput ───────────────────────────────────────────────────────────


class TestRevisaoInput:
    def test_valido(self):
        obj = RevisaoInput(numero_aula=1, numero_revisao=2)
        assert obj.numero_revisao == 2

    def test_revisao_invalida(self):
        with pytest.raises(ValidationError):
            RevisaoInput(numero_aula=1, numero_revisao=4)

    def test_aula_invalida(self):
        with pytest.raises(ValidationError):
            RevisaoInput(numero_aula=9, numero_revisao=1)


# ── RegistrarSessaoInglesInput ─────────────────────────────────────────────


class TestRegistrarSessaoInglesInput:
    def test_tipo_valido(self):
        obj = RegistrarSessaoInglesInput(
            tipo="podcast", descricao="Ouvi Syntax.fm", duracao_minutos=30
        )
        assert obj.tipo == "podcast"

    def test_tipo_invalido(self):
        with pytest.raises(ValidationError):
            RegistrarSessaoInglesInput(tipo="gaming", descricao="x", duracao_minutos=30)

    def test_duracao_zero(self):
        with pytest.raises(ValidationError):
            RegistrarSessaoInglesInput(tipo="escrita", descricao="x", duracao_minutos=0)

    def test_duracao_maxima(self):
        with pytest.raises(ValidationError):
            RegistrarSessaoInglesInput(tipo="leitura", descricao="x", duracao_minutos=500)


# ── RegistrarEstudoCSInput ─────────────────────────────────────────────────


class TestRegistrarEstudoCSInput:
    def test_area_valida(self):
        obj = RegistrarEstudoCSInput(area="agentes", topico="LangGraph", duracao_minutos=60)
        assert obj.area == "agentes"

    def test_area_invalida(self):
        with pytest.raises(ValidationError):
            RegistrarEstudoCSInput(area="frontend", topico="React", duracao_minutos=60)

    def test_status_invalido(self):
        with pytest.raises(ValidationError):
            RegistrarEstudoCSInput(
                area="agentes", topico="LangGraph", duracao_minutos=60, status="completo"
            )

    def test_todos_status_validos(self):
        for status in ["estudado", "revisando", "dominado"]:
            obj = RegistrarEstudoCSInput(
                area="agentes", topico="RAG", duracao_minutos=30, status=status
            )
            assert obj.status == status


# ── RegistrarModuloAWSInput ───────────────────────────────────────────────


class TestRegistrarModuloAWSInput:
    def test_valido(self):
        obj = RegistrarModuloAWSInput(topico="IAM", duracao_minutos=60)
        assert obj.status == "concluido"

    def test_status_invalido(self):
        with pytest.raises(ValidationError):
            RegistrarModuloAWSInput(topico="IAM", duracao_minutos=60, status="feito")


# ── RegistrarModuloDCInput ────────────────────────────────────────────────


class TestRegistrarModuloDCInput:
    def test_trilha_valida(self):
        obj = RegistrarModuloDCInput(curso="Python", modulo="Python Basics", duracao_minutos=30)
        assert obj.curso == "Python"

    def test_trilha_invalida(self):
        with pytest.raises(ValidationError):
            RegistrarModuloDCInput(curso="JavaScript", modulo="x", duracao_minutos=30)

    def test_todas_trilhas_validas(self):
        for trilha in ["Python", "Machine Learning", "Data Engineering", "AI & LLMs"]:
            obj = RegistrarModuloDCInput(curso=trilha, modulo="Módulo X", duracao_minutos=30)
            assert obj.curso == trilha


# ── RegistrarDuvidaCursoInput ─────────────────────────────────────────────


class TestRegistrarDuvidaCursoInput:
    def test_plataforma_valida(self):
        obj = RegistrarDuvidaCursoInput(
            plataforma="aws", topico="VPC", duvida="O que é subnetting?"
        )
        assert obj.plataforma == "aws"

    def test_plataforma_invalida(self):
        with pytest.raises(ValidationError):
            RegistrarDuvidaCursoInput(plataforma="udemy", topico="x", duvida="dúvida")

    def test_duvida_muito_curta(self):
        with pytest.raises(ValidationError):
            RegistrarDuvidaCursoInput(plataforma="aws", topico="VPC", duvida="x")


# ── RegistrarXPAWSInput ───────────────────────────────────────────────────


class TestRegistrarXPAWSInput:
    def test_tipo_valido(self):
        obj = RegistrarXPAWSInput(tipo="aws_topico", descricao="IAM concluído")
        assert obj.tipo == "aws_topico"

    def test_tipo_invalido(self):
        with pytest.raises(ValidationError):
            RegistrarXPAWSInput(tipo="aws_video", descricao="x")

    def test_todos_tipos_validos(self):
        for tipo in ["aws_topico", "aws_sessao", "datacamp_modulo"]:
            obj = RegistrarXPAWSInput(tipo=tipo, descricao="descrição")
            assert obj.tipo == tipo


# ── RegistrarXPCSInput ────────────────────────────────────────────────────


class TestRegistrarXPCSInput:
    def test_tipo_valido(self):
        obj = RegistrarXPCSInput(tipo="leetcode_easy", descricao="Two Sum")
        assert obj.tipo == "leetcode_easy"

    def test_dificuldade_invalida(self):
        with pytest.raises(ValidationError):
            RegistrarXPCSInput(tipo="leetcode_easy", descricao="x", dificuldade="ultra")

    def test_dificuldades_validas(self):
        for dif in ["easy", "medium", "hard", ""]:
            obj = RegistrarXPCSInput(tipo="cs_topico", descricao="xyz", dificuldade=dif)
            assert obj.dificuldade == dif


# ── AgendarSessaoInput ────────────────────────────────────────────────────


class TestAgendarSessaoInput:
    def test_valido(self):
        obj = AgendarSessaoInput(
            tipo="aws",
            titulo="Estudar IAM",
            descricao="Revisar policies e roles",
            data_inicio="2026-05-07 09:00",
        )
        assert obj.duracao_minutos == 60

    def test_data_formato_invalido(self):
        with pytest.raises(ValidationError):
            AgendarSessaoInput(
                tipo="aws",
                titulo="Estudar",
                descricao="x",
                data_inicio="07/05/2026 09:00",
            )

    def test_tipo_invalido(self):
        with pytest.raises(ValidationError):
            AgendarSessaoInput(
                tipo="netflix",
                titulo="x",
                descricao="x",
                data_inicio="2026-05-07 09:00",
            )

    def test_duracao_minima(self):
        with pytest.raises(ValidationError):
            AgendarSessaoInput(
                tipo="aws",
                titulo="x",
                descricao="x",
                data_inicio="2026-05-07 09:00",
                duracao_minutos=10,  # mínimo é 15
            )
