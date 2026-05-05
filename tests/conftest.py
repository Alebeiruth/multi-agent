"""
conftest.py — Fixtures compartilhadas entre todos os testes.

Cada fixture que manipula storage usa um arquivo temporário isolado
via tmp_path do pytest — os testes nunca tocam nos dados reais.
"""

import json

import pytest

# ── Fixture: storage temporário por tool ──────────────────────────────────


@pytest.fixture
def tmp_storage_estatistica(tmp_path, monkeypatch):
    """Redireciona o storage de estatística para um arquivo temporário."""
    import tools.estatistica_tool as mod

    tmp_file = str(tmp_path / "estatistica.json")
    monkeypatch.setattr(mod, "STORAGE_FILE", tmp_file)
    return tmp_file


@pytest.fixture
def tmp_storage_ingles(tmp_path, monkeypatch):
    """Redireciona o storage de inglês para um arquivo temporário."""
    import tools.ingles_tool as mod

    tmp_file = str(tmp_path / "ingles.json")
    monkeypatch.setattr(mod, "STORAGE_FILE", tmp_file)
    return tmp_file


@pytest.fixture
def tmp_storage_computacao(tmp_path, monkeypatch):
    """Redireciona o storage de computação para um arquivo temporário."""
    import tools.computacao_tool as mod

    tmp_file = str(tmp_path / "computacao.json")
    monkeypatch.setattr(mod, "STORAGE_FILE", tmp_file)
    return tmp_file


@pytest.fixture
def tmp_storage_aws(tmp_path, monkeypatch):
    """Redireciona o storage de AWS para um arquivo temporário."""
    import tools.aws_tool as mod

    tmp_file = str(tmp_path / "aws.json")
    monkeypatch.setattr(mod, "STORAGE_FILE", tmp_file)
    return tmp_file


@pytest.fixture
def tmp_storage_gamification(tmp_path, monkeypatch):
    """Redireciona o storage de gamificação para um arquivo temporário."""
    import tools.gamification_tool as mod

    tmp_file = str(tmp_path / "gamification.json")
    monkeypatch.setattr(mod, "STORAGE_FILE", tmp_file)
    return tmp_file


# ── Fixture: aula pré-registrada ──────────────────────────────────────────


@pytest.fixture
def aula_registrada(tmp_storage_estatistica):
    """Cria uma aula já registrada no storage para testes que dependem disso."""
    from tools.estatistica_tool import registrar_aula

    registrar_aula.invoke(
        {
            "numero": 1,
            "tema": "Distribuição Normal",
            "conteudos": "média, variância, desvio padrão",
            "data_aula": "2026-05-07",
            "observacoes": "",
        }
    )
    return {"numero": 1, "tema": "Distribuição Normal", "data_aula": "2026-05-07"}


# ── Fixture: módulo AWS pré-registrado ────────────────────────────────────


@pytest.fixture
def modulo_aws_registrado(tmp_storage_aws):
    """Cria um módulo AWS já registrado para testes de progresso."""
    from tools.aws_tool import registrar_modulo_aws

    registrar_modulo_aws.invoke(
        {
            "topico": "IAM — Users, Groups, Roles e Policies",
            "duracao_minutos": 60,
            "status": "concluido",
            "observacoes": "",
        }
    )
    return {"topico": "IAM — Users, Groups, Roles e Policies"}
