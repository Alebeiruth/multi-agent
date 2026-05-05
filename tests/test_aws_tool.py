"""
Testes unitários para tools/aws_tool.py

Cobertura:
- registrar_modulo_aws: happy path, validação, progresso
- registrar_modulo_datacamp: happy path, trilha inválida
- consultar_progresso_aws_datacamp: vazio, com dados
- sugerir_proximo_aws_datacamp: sugestão por plataforma, automática
- registrar_duvida_curso / listar_duvidas_curso: CRUD básico
"""

import json
import pytest
from tools.aws_tool import (
    registrar_modulo_aws,
    registrar_modulo_datacamp,
    consultar_progresso_aws_datacamp,
    sugerir_proximo_aws_datacamp,
    registrar_duvida_curso,
    listar_duvidas_curso,
)


# ── registrar_modulo_aws ───────────────────────────────────────────────────

class TestRegistrarModuloAWS:

    def test_registra_com_sucesso(self, tmp_storage_aws):
        result = registrar_modulo_aws.invoke({
            "topico": "IAM — Users, Groups, Roles e Policies",
            "duracao_minutos": 60,
            "status": "concluido",
            "observacoes": "",
        })
        assert "✅" in result
        assert "IAM" in result

    def test_persiste_no_storage(self, tmp_storage_aws):
        registrar_modulo_aws.invoke({
            "topico": "EC2 — Instâncias, Tipos e Pricing",
            "duracao_minutos": 45,
            "status": "concluido",
            "observacoes": "",
        })
        with open(tmp_storage_aws, "r") as f:
            data = json.load(f)
        assert len(data["modulos_aws"]) == 1

    def test_mostra_progresso_percentual(self, tmp_storage_aws):
        result = registrar_modulo_aws.invoke({
            "topico": "IAM — Users, Groups, Roles e Policies",
            "duracao_minutos": 60,
            "status": "concluido",
            "observacoes": "",
        })
        assert "%" in result

    def test_valida_status_invalido(self, tmp_storage_aws):
        result = registrar_modulo_aws.invoke({
            "topico": "IAM — Users, Groups, Roles e Policies",
            "duracao_minutos": 60,
            "status": "feito",  # inválido
            "observacoes": "",
        })
        assert "validação" in result.lower()

    def test_valida_duracao_zero(self, tmp_storage_aws):
        result = registrar_modulo_aws.invoke({
            "topico": "IAM",
            "duracao_minutos": 0,  # inválido
            "status": "concluido",
            "observacoes": "",
        })
        assert "validação" in result.lower()


# ── registrar_modulo_datacamp ─────────────────────────────────────────────

class TestRegistrarModuloDatacamp:

    def test_registra_com_sucesso(self, tmp_storage_aws):
        result = registrar_modulo_datacamp.invoke({
            "curso": "Python",
            "modulo": "Python Basics",
            "duracao_minutos": 30,
            "status": "concluido",
            "observacoes": "",
        })
        assert "✅" in result
        assert "Python" in result

    def test_valida_trilha_invalida(self, tmp_storage_aws):
        result = registrar_modulo_datacamp.invoke({
            "curso": "JavaScript",  # não existe
            "modulo": "Módulo X",
            "duracao_minutos": 30,
            "status": "concluido",
            "observacoes": "",
        })
        assert "validação" in result.lower()

    def test_mostra_progresso_da_trilha(self, tmp_storage_aws):
        result = registrar_modulo_datacamp.invoke({
            "curso": "Machine Learning",
            "modulo": "Supervised Learning with scikit-learn",
            "duracao_minutos": 60,
            "status": "concluido",
            "observacoes": "",
        })
        assert "Machine Learning" in result
        assert "%" in result


# ── consultar_progresso_aws_datacamp ──────────────────────────────────────

class TestConsultarProgresso:

    def test_retorna_mensagem_quando_vazio(self, tmp_storage_aws):
        result = consultar_progresso_aws_datacamp.invoke({})
        assert "0" in result or "AWS" in result

    def test_mostra_progresso_com_dados(self, modulo_aws_registrado):
        result = consultar_progresso_aws_datacamp.invoke({})
        assert "AWS" in result
        assert "IAM" in result or "1/" in result


# ── sugerir_proximo_aws_datacamp ──────────────────────────────────────────

class TestSugerirProximo:

    def test_sugere_aws(self, tmp_storage_aws):
        result = sugerir_proximo_aws_datacamp.invoke({"plataforma": "aws"})
        assert "AWS SAA" in result
        assert "📌" in result

    def test_sugere_datacamp(self, tmp_storage_aws):
        result = sugerir_proximo_aws_datacamp.invoke({"plataforma": "datacamp"})
        assert "Datacamp" in result
        assert "📌" in result

    def test_sugestao_automatica(self, tmp_storage_aws):
        result = sugerir_proximo_aws_datacamp.invoke({"plataforma": ""})
        assert "📌" in result

    def test_avanca_apos_modulo_concluido(self, modulo_aws_registrado):
        result = sugerir_proximo_aws_datacamp.invoke({"plataforma": "aws"})
        # IAM já foi registrado, próximo deve ser diferente
        assert "IAM — Users, Groups, Roles e Policies" not in result


# ── registrar_duvida_curso / listar_duvidas_curso ─────────────────────────

class TestDuvidasCurso:

    def test_registra_duvida_aws(self, tmp_storage_aws):
        result = registrar_duvida_curso.invoke({
            "plataforma": "aws",
            "topico": "VPC Peering",
            "duvida": "Qual a diferença entre VPC Peering e Transit Gateway?",
        })
        assert "📝" in result
        assert "VPC Peering" in result

    def test_lista_duvidas_pendentes(self, tmp_storage_aws):
        registrar_duvida_curso.invoke({
            "plataforma": "datacamp",
            "topico": "Random Forest",
            "duvida": "Como escolher o número de árvores?",
        })
        result = listar_duvidas_curso.invoke({})
        assert "Random Forest" in result

    def test_lista_vazia(self, tmp_storage_aws):
        result = listar_duvidas_curso.invoke({})
        assert "pendente" in result.lower() or "🎯" in result

    def test_valida_plataforma_invalida(self, tmp_storage_aws):
        result = registrar_duvida_curso.invoke({
            "plataforma": "udemy",  # inválido
            "topico": "Tópico X",
            "duvida": "Dúvida sobre algo.",
        })
        assert "validação" in result.lower()