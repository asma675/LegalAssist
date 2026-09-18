from sqlalchemy import or_
from sqlalchemy.orm import Session
from .models import CorpusDocument

def retrieve(db: Session, query: str, jurisdiction: str = "Canada", top_k: int = 8):
    terms = [t.strip('.,:;!?()[]').lower() for t in query.split() if len(t) > 3][:12]
    q = db.query(CorpusDocument)
    if jurisdiction and jurisdiction.lower() != "all":
        # Federal materials remain relevant to province-specific searches.
        q = q.filter(or_(CorpusDocument.jurisdiction.ilike(f"%{jurisdiction.split(',')[0]}%"), CorpusDocument.jurisdiction.ilike("%Canada%")))
    docs = q.limit(500).all()
    scored = []
    for d in docs:
        hay = f"{d.title} {d.citation or ''} {d.text_content}".lower()
        score = sum(hay.count(t) for t in terms)
        if score:
            scored.append((score, d))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [d for _, d in scored[:top_k]] or docs[:min(top_k, len(docs))]
