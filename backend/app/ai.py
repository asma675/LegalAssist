from openai import OpenAI
from .config import settings

SYSTEM = """You are Rafi, an AI legal-work assistant for licensed legal professionals and supervised legal teams in Canada.
You provide legal information, research assistance, document analysis, drafting assistance, and workflow support. You do not represent the user, form a lawyer-client relationship, or make final legal decisions.
Never invent an authority, quotation, citation, fact, deadline, or source. When sources are supplied, cite only those sources using their exact [S#] labels. Distinguish sourced facts from inference. If authority is insufficient, say so clearly and recommend verification by a qualified legal professional.
Treat all generated work product as a draft requiring human review before reliance, filing, delivery, or execution."""

def synthesize(prompt: str, sources: list[dict] | None = None):
    sources = sources or []
    context = "\n\n".join([f"[S{i+1}] {s['title']} | {s.get('citation','')} | {s.get('text','')} | {s.get('url','')}" for i,s in enumerate(sources)])
    if not settings.openai_api_key:
        if sources:
            bullets = "\n".join([f"- [S{i+1}] {s['title']} ({s.get('citation') or 'source'})" for i,s in enumerate(sources[:6])])
            return f"Demo-mode research brief for: **{prompt}**\n\nRelevant verified corpus items:\n{bullets}\n\nRafi is running without an AI API key, so no synthesized legal conclusion has been generated. Review the linked authorities and enable OPENAI_API_KEY for source-grounded drafting."
        return "Rafi is running in demo mode. Connect an AI provider to generate source-grounded analysis. No legal conclusion has been generated."
    client = OpenAI(api_key=settings.openai_api_key)
    msg = f"USER REQUEST:\n{prompt}\n\nAUTHORIZED SOURCES:\n{context or 'No authoritative source material was retrieved. Do not invent citations.'}"
    res = client.responses.create(model=settings.openai_model, instructions=SYSTEM, input=msg)
    return res.output_text
