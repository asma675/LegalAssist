from __future__ import annotations

from collections import defaultdict

from openai import OpenAI
from sqlalchemy import or_
from sqlalchemy.orm import Session

from .config import settings
from .models import CorpusChunk, CorpusDocument


def _terms(query: str) -> list[str]:
    return [
        t.strip(".,:;!?()[]{}\"'").lower()
        for t in query.split()
        if len(t.strip(".,:;!?()[]{}\"'")) > 3
    ][:16]


def _scope(q, jurisdiction: str):
    if jurisdiction and jurisdiction.lower() != "all":
        primary = jurisdiction.split(",")[0].strip()
        q = q.filter(
            or_(
                CorpusDocument.jurisdiction.ilike(f"%{primary}%"),
                CorpusDocument.jurisdiction.ilike("%Canada%"),
            )
        )
    return q


def _keyword_rank(db: Session, query: str, jurisdiction: str, limit: int) -> list[CorpusDocument]:
    terms = _terms(query)
    q = _scope(db.query(CorpusDocument), jurisdiction)
    docs = q.limit(800).all()
    scored: list[tuple[float, CorpusDocument]] = []
    for d in docs:
        title = (d.title or "").lower()
        citation = (d.citation or "").lower()
        body = (d.text_content or "").lower()
        score = 0.0
        for term in terms:
            score += title.count(term) * 5.0
            score += citation.count(term) * 6.0
            score += body.count(term)
        if score:
            scored.append((score, d))
    scored.sort(key=lambda x: x[0], reverse=True)
    ranked = [d for _, d in scored[:limit]]
    if not ranked:
        ranked = docs[:limit]
    for rank, d in enumerate(ranked, start=1):
        d._rag_mode = "keyword"
        d._rag_rank = rank
        d._rag_text = (d.text_content or "")[:1800]
    return ranked


def _embed_query(query: str) -> list[float] | None:
    if not settings.openai_api_key:
        return None
    try:
        client = OpenAI(api_key=settings.openai_api_key)
        res = client.embeddings.create(
            model=settings.openai_embedding_model,
            input=query,
            dimensions=settings.openai_embedding_dimensions,
        )
        return res.data[0].embedding
    except Exception:
        return None


def _vector_rank(
    db: Session,
    query_embedding: list[float],
    jurisdiction: str,
    limit: int,
) -> list[tuple[CorpusDocument, CorpusChunk]]:
    q = (
        db.query(CorpusDocument, CorpusChunk)
        .join(CorpusChunk, CorpusChunk.corpus_document_id == CorpusDocument.id)
        .filter(CorpusChunk.embedding.is_not(None))
    )
    q = _scope(q, jurisdiction)
    distance = CorpusChunk.embedding.cosine_distance(query_embedding)
    rows = q.order_by(distance).limit(limit).all()

    out: list[tuple[CorpusDocument, CorpusChunk]] = []
    seen_docs: set[int] = set()
    for doc, chunk in rows:
        if doc.id in seen_docs:
            continue
        seen_docs.add(doc.id)
        out.append((doc, chunk))
    return out


def retrieve(db: Session, query: str, jurisdiction: str = "Canada", top_k: int = 8):
    """Hybrid RAG retrieval using pgvector + keyword Reciprocal Rank Fusion.

    If query embeddings are unavailable, retrieval safely falls back to the
    deterministic keyword retriever instead of failing the request.
    """
    top_k = max(1, min(int(top_k), 20))
    keyword_docs = _keyword_rank(db, query, jurisdiction, max(top_k * 4, 20))
    query_embedding = _embed_query(query)

    if not query_embedding:
        return keyword_docs[:top_k]

    try:
        vector_rows = _vector_rank(db, query_embedding, jurisdiction, max(top_k * 4, 20))
    except Exception:
        return keyword_docs[:top_k]

    if not vector_rows:
        return keyword_docs[:top_k]

    scores: defaultdict[int, float] = defaultdict(float)
    docs: dict[int, CorpusDocument] = {}
    best_chunk: dict[int, CorpusChunk] = {}

    rrf_k = 60.0
    for rank, d in enumerate(keyword_docs, start=1):
        docs[d.id] = d
        scores[d.id] += 1.0 / (rrf_k + rank)

    for rank, (d, chunk) in enumerate(vector_rows, start=1):
        docs[d.id] = d
        best_chunk[d.id] = chunk
        scores[d.id] += 1.0 / (rrf_k + rank)

    ranked_ids = sorted(scores, key=scores.get, reverse=True)[:top_k]
    result: list[CorpusDocument] = []
    for rank, doc_id in enumerate(ranked_ids, start=1):
        d = docs[doc_id]
        chunk = best_chunk.get(doc_id)
        d._rag_mode = "hybrid_vector_keyword"
        d._rag_rank = rank
        d._rag_score = round(scores[doc_id], 6)
        d._rag_chunk_id = chunk.id if chunk else None
        d._rag_text = (chunk.text_content if chunk else d.text_content or "")[:1800]
        result.append(d)

    return result
