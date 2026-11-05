"""Print a concise RAG readiness report."""
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.config import settings
from app.db import SessionLocal
from app.models import CorpusChunk, CorpusDocument


def main():
    db = SessionLocal()
    try:
        docs = db.query(CorpusDocument).count()
        chunks = db.query(CorpusChunk).count()
        embedded = db.query(CorpusChunk).filter(CorpusChunk.embedding.is_not(None)).count()
        mode = "hybrid_vector_keyword" if embedded else "keyword_fallback"
        print("Rafi RAG status")
        print(f"documents: {docs}")
        print(f"chunks: {chunks}")
        print(f"embedded_chunks: {embedded}")
        print(f"embedding_model: {settings.openai_embedding_model}")
        print(f"embedding_dimensions: {settings.openai_embedding_dimensions}")
        print(f"vector_ready: {bool(embedded)}")
        print(f"retrieval: {mode}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
