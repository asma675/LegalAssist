"""Chunk the authorized corpus and create pgvector embeddings.

Usage:
  python scripts/reindex_corpus.py
  python scripts/reindex_corpus.py --limit 100

The script is idempotent: it replaces existing chunks for each indexed document.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from openai import OpenAI
from sqlalchemy import text

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.config import settings
from app.db import Base, SessionLocal, engine
from app.models import CorpusChunk, CorpusDocument


def chunk_text(text_value: str, target_chars: int = 3600, overlap_chars: int = 500) -> list[str]:
    clean = re.sub(r"\s+", " ", text_value or "").strip()
    if not clean:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(clean):
        end = min(len(clean), start + target_chars)
        if end < len(clean):
            split = clean.rfind(". ", start + target_chars // 2, end)
            if split > start:
                end = split + 1
        piece = clean[start:end].strip()
        if piece:
            chunks.append(piece)
        if end >= len(clean):
            break
        start = max(end - overlap_chars, start + 1)
    return chunks


def embed_batch(client: OpenAI, texts: list[str]) -> list[list[float]]:
    res = client.embeddings.create(
        model=settings.openai_embedding_model,
        input=texts,
        dimensions=settings.openai_embedding_dimensions,
    )
    return [item.embedding for item in res.data]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0, help="Maximum number of corpus documents to index")
    parser.add_argument("--batch-size", type=int, default=32)
    args = parser.parse_args()

    if not settings.openai_api_key:
        raise SystemExit("OPENAI_API_KEY is required to create embeddings.")

    if engine.dialect.name == "postgresql":
        with engine.begin() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    Base.metadata.create_all(bind=engine)

    client = OpenAI(api_key=settings.openai_api_key)
    db = SessionLocal()
    try:
        q = db.query(CorpusDocument).order_by(CorpusDocument.id)
        if args.limit:
            q = q.limit(args.limit)
        docs = q.all()

        indexed_docs = 0
        total_chunks = 0
        for doc in docs:
            chunks = chunk_text(doc.text_content)
            db.query(CorpusChunk).filter(CorpusChunk.corpus_document_id == doc.id).delete(
                synchronize_session=False
            )
            db.flush()

            for offset in range(0, len(chunks), args.batch_size):
                batch = chunks[offset : offset + args.batch_size]
                vectors = embed_batch(client, batch)
                for i, (chunk, embedding) in enumerate(zip(batch, vectors), start=offset):
                    db.add(
                        CorpusChunk(
                            corpus_document_id=doc.id,
                            chunk_index=i,
                            text_content=chunk,
                            token_estimate=max(1, len(chunk) // 4),
                            embedding=embedding,
                        )
                    )
            db.commit()
            indexed_docs += 1
            total_chunks += len(chunks)
            print(f"[{indexed_docs}/{len(docs)}] {doc.title}: {len(chunks)} chunks")

        print(f"Indexed {indexed_docs} documents into {total_chunks} embedded chunks.")
        print(f"Embedding model: {settings.openai_embedding_model}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
