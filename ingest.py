import os
import shutil
import argparse
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import fitz


# ── Configuração das coleções ──────────────────────────────────────────────

COLECOES = {
    "artigos": {
        "data_dir":    "data/articles",
        "chroma_dir":  "./chroma_db",
        "collection":  "artigos",
        "descricao":   "Artigos científicos (coach original)",
    },
    "estatistica": {
        "data_dir":    "data/estatistica",
        "chroma_dir":  "./chroma_db_estatistica",
        "collection":  "estatistica",
        "descricao":   "PDFs das aulas de Estatística e Probabilidade",
    },
}


# ── Funções base ───────────────────────────────────────────────────────────

def load_pdfs(directory: str) -> list[dict]:
    """Carrega todos os PDFs de um diretório e extrai o texto."""
    docs = []
    pasta = Path(directory)

    if not pasta.exists():
        print(f"  ⚠️  Pasta '{directory}' não encontrada.")
        return docs

    for path in sorted(pasta.glob("*.pdf")):
        try:
            doc = fitz.open(str(path))
            text = "\n".join(page.get_text() for page in doc)
            docs.append({"text": text, "source": path.name})
            print(f"  📄 {path.name} — {len(text):,} caracteres")
        except Exception as e:
            print(f"  ❌ Erro ao ler {path.name}: {e}")

    return docs


def chunk_docs(docs: list[dict], chunk_size: int = 1024, chunk_overlap: int = 100) -> list:
    """
    Divide os documentos em chunks para indexação.

    chunk_size: tamanho máximo de cada chunk em caracteres.
    chunk_overlap: sobreposição entre chunks consecutivos — garante que
                   contexto não seja perdido nas bordas de cada divisão.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    chunks = []
    for doc in docs:
        splits = splitter.create_documents(
            texts=[doc["text"]],
            metadatas=[{"source": doc["source"]}],
        )
        chunks.extend(splits)
    return chunks


def build_embeddings() -> HuggingFaceEmbeddings:
    """Inicializa o modelo de embeddings (compartilhado entre coleções)."""
    print("\n🔧 Carregando modelo de embeddings BAAI/bge-large-en-v1.5...")
    return HuggingFaceEmbeddings(
        model_name="BAAI/bge-large-en-v1.5",
        model_kwargs={"device": "cpu"},
    )


def ingest_colecao(nome: str, config: dict, embeddings: HuggingFaceEmbeddings):
    """Indexa uma coleção específica no ChromaDB."""
    print(f"\n{'═' * 50}")
    print(f"  📚 Indexando: {config['descricao']}")
    print(f"  Pasta:  {config['data_dir']}")
    print(f"  Chroma: {config['chroma_dir']}")
    print(f"{'─' * 50}")

    docs = load_pdfs(config["data_dir"])

    if not docs:
        print(f"  ⚠️  Nenhum PDF encontrado em '{config['data_dir']}'. Pulando.")
        return

    chunks = chunk_docs(docs)
    print(f"\n  ✂️  {len(chunks)} chunks gerados de {len(docs)} arquivo(s).")

    # deleta o índice existente para garantir consistência
    if os.path.exists(config["chroma_dir"]):
        shutil.rmtree(config["chroma_dir"])
        print(f"  🗑️  Índice anterior removido.")

    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=config["chroma_dir"],
        collection_name=config["collection"],
    )

    print(f"  ✅ {len(chunks)} chunks indexados em '{config['chroma_dir']}'.")


# ── Entry point ────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Pipeline de indexação de PDFs para o Multi-Agent Study Coach."
    )
    parser.add_argument(
        "--colecao",
        choices=list(COLECOES.keys()) + ["todas"],
        default="todas",
        help="Coleção a indexar. Padrão: todas.",
    )
    args = parser.parse_args()

    print("\n🚀 Multi-Agent Study Coach — Pipeline de Indexação")

    embeddings = build_embeddings()

    if args.colecao == "todas":
        for nome, config in COLECOES.items():
            ingest_colecao(nome, config, embeddings)
    else:
        config = COLECOES[args.colecao]
        ingest_colecao(args.colecao, config, embeddings)

    print(f"\n{'═' * 50}")
    print("  🎉 Indexação concluída!")
    print(f"{'═' * 50}\n")


if __name__ == "__main__":
    main()