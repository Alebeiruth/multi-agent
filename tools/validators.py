"""
validators.py — Modelos Pydantic centralizados para validação de inputs das tools.

Cada tool valida seus inputs instanciando o modelo correspondente no início
da função. Se a validação falhar, Pydantic lança ValidationError com mensagem
clara antes de qualquer operação de I/O.
"""

from datetime import date
from typing import Literal
from pydantic import BaseModel, Field, field_validator, model_validator


# ── Estatística ────────────────────────────────────────────────────────────

class RegistrarAulaInput(BaseModel):
    numero: int = Field(..., ge=1, le=8, description="Número da aula (1 a 8)")
    tema: str = Field(..., min_length=3, max_length=200, description="Tema da aula")
    conteudos: str = Field(..., min_length=3, description="Conteúdos abordados")
    data_aula: str = Field(default="", description="Data no formato YYYY-MM-DD")
    observacoes: str = Field(default="", max_length=500)

    @field_validator("data_aula")
    @classmethod
    def validar_data(cls, v: str) -> str:
        if not v:
            return v
        try:
            date.fromisoformat(v)
        except ValueError as err:
            raise ValueError(f"data_aula '{v}' inválida. Use o formato YYYY-MM-DD.") from err
        return v


class RevisaoInput(BaseModel):
    numero_aula: int = Field(..., ge=1, le=8)
    numero_revisao: int = Field(..., ge=1, le=3)


# ── Inglês ─────────────────────────────────────────────────────────────────

TipoSessaoIngles = Literal["escrita", "fala", "podcast", "youtube", "vocabulario", "leitura"]

class RegistrarSessaoInglesInput(BaseModel):
    tipo: TipoSessaoIngles
    descricao: str = Field(..., min_length=3, max_length=300)
    duracao_minutos: int = Field(..., ge=1, le=480, description="Máximo 8 horas por sessão")
    observacoes: str = Field(default="", max_length=500)


class AdicionarVocabularioInput(BaseModel):
    palavra: str = Field(..., min_length=1, max_length=100)
    traducao: str = Field(..., min_length=1, max_length=200)
    exemplo: str = Field(..., min_length=5, max_length=300)
    categoria: str = Field(default="geral", max_length=50)


TipoEscrita = Literal["email", "essay", "summary", "dialogue", "linkedin"]

class GerarPromptEscritaInput(BaseModel):
    tipo: TipoEscrita = Field(default="email")
    contexto: str = Field(default="", max_length=300)


# ── Computação ─────────────────────────────────────────────────────────────

AreaCS = Literal["cs_fundamentals", "agentes"]
StatusEstudo = Literal["estudado", "revisando", "dominado"]

class RegistrarEstudoCSInput(BaseModel):
    area: AreaCS
    topico: str = Field(..., min_length=3, max_length=200)
    duracao_minutos: int = Field(..., ge=1, le=480)
    status: StatusEstudo = Field(default="estudado")
    observacoes: str = Field(default="", max_length=500)


class RegistrarDuvidaInput(BaseModel):
    topico: str = Field(..., min_length=3, max_length=200)
    duvida: str = Field(..., min_length=5, max_length=500)
    area: AreaCS = Field(default="cs_fundamentals")


# ── AWS / Datacamp ─────────────────────────────────────────────────────────

StatusModuloAWS = Literal["concluido", "revisando", "com_duvidas"]
StatusModuloDC  = Literal["concluido", "em_andamento", "revisando"]
TrilhaDatacamp  = Literal["Python", "Machine Learning", "Data Engineering", "AI & LLMs"]
PlataformaCurso = Literal["aws", "datacamp"]

class RegistrarModuloAWSInput(BaseModel):
    topico: str = Field(..., min_length=3, max_length=200)
    duracao_minutos: int = Field(..., ge=1, le=480)
    status: StatusModuloAWS = Field(default="concluido")
    observacoes: str = Field(default="", max_length=500)


class RegistrarModuloDCInput(BaseModel):
    curso: TrilhaDatacamp
    modulo: str = Field(..., min_length=3, max_length=200)
    duracao_minutos: int = Field(..., ge=1, le=480)
    status: StatusModuloDC = Field(default="concluido")
    observacoes: str = Field(default="", max_length=500)


class RegistrarDuvidaCursoInput(BaseModel):
    plataforma: PlataformaCurso
    topico: str = Field(..., min_length=3, max_length=200)
    duvida: str = Field(..., min_length=5, max_length=500)


# ── Gamificação ────────────────────────────────────────────────────────────

TipoXPAWS = Literal["aws_topico", "aws_sessao", "datacamp_modulo"]
TipoXPCS  = Literal["cs_topico", "agentes_topico", "leetcode_easy", "leetcode_medium", "leetcode_hard"]

class RegistrarXPAWSInput(BaseModel):
    tipo: TipoXPAWS
    descricao: str = Field(..., min_length=3, max_length=200)


class RegistrarXPCSInput(BaseModel):
    tipo: TipoXPCS
    descricao: str = Field(..., min_length=3, max_length=200)
    dificuldade: str = Field(default="")

    @field_validator("dificuldade")
    @classmethod
    def validar_dificuldade(cls, v: str) -> str:
        if v and v not in {"easy", "medium", "hard"}:
            raise ValueError(f"dificuldade '{v}' inválida. Use: easy, medium, hard.")
        return v


# ── Calendar ───────────────────────────────────────────────────────────────

TipoSessaoCalendar = Literal["leetcode", "artigo", "estatistica", "aws", "datacamp"]

class AgendarSessaoInput(BaseModel):
    tipo: TipoSessaoCalendar
    titulo: str = Field(..., min_length=3, max_length=200)
    descricao: str = Field(..., min_length=3, max_length=1000)
    data_inicio: str = Field(..., description="Formato: YYYY-MM-DD HH:MM")
    duracao_minutos: int = Field(default=60, ge=15, le=480)

    @field_validator("data_inicio")
    @classmethod
    def validar_data_inicio(cls, v: str) -> str:
        from datetime import datetime
        try:
            datetime.strptime(v, "%Y-%m-%d %H:%M")
        except ValueError as err:
            raise ValueError(f"data_inicio '{v}' inválida. Use o formato: YYYY-MM-DD HH:MM") from err
        return v