"""Evaluate retrieval with labeled queries.

Evaluation JSON format:
[
  {
    "query": "What is the duty of honest performance?",
    "jurisdiction": "Canada",
    "relevant_citations": ["2014 SCC 71"]
  }
]

Reports HitRate@5 and MRR. Only use measured results in a resume/interview.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.db import SessionLocal
from app.rag import retrieve


def norm(value: str | None) -> str:
    return (value or "").strip().lower()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default="evaluation/retrieval_queries.json")
    parser.add_argument("--k", type=int, default=5)
    args = parser.parse_args()

    path = Path(args.file)
    if not path.is_absolute():
        path = Path(__file__).resolve().parents[1] / path
    cases = json.loads(path.read_text(encoding="utf-8"))
    if not cases:
        raise SystemExit("No evaluation cases found.")

    db = SessionLocal()
    hits = 0
    rr_total = 0.0
    try:
        for i, case in enumerate(cases, start=1):
            docs = retrieve(
                db,
                case["query"],
                case.get("jurisdiction", "Canada"),
                max(args.k, 10),
            )
            expected = {norm(x) for x in case.get("relevant_citations", [])}
            rank = None
            for pos, doc in enumerate(docs[: args.k], start=1):
                if norm(doc.citation) in expected:
                    rank = pos
                    break
            if rank:
                hits += 1
                rr_total += 1.0 / rank
            print(
                f"{i:02d}. {'HIT' if rank else 'MISS'}"
                f" rank={rank or '-'} | {case['query']}"
            )

        n = len(cases)
        print(f"\nqueries: {n}")
        print(f"HitRate@{args.k}: {hits / n:.3f}")
        print(f"MRR@{args.k}: {rr_total / n:.3f}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
