import re
from datetime import datetime
from sqlalchemy.orm import Session
from .models import (
    Matter, Document, DocumentPage, Task, Event, CorpusDocument, MatterFact, Claim,
    EvidenceLink, LegalIssue, IssueAuthority, MatterDeadline, MissingInformation,
    Recommendation, MatterDigest, IntelligenceRun, FirmPlaybook
)
from .rag import retrieve

DATE_PATTERNS = [
    r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}\b",
    r"\b\d{4}-\d{2}-\d{2}\b",
]

PRACTICE_ISSUES = {
    "employment": [
        ("Termination date and notice", "Confirm the effective termination date, notice position, and documentary consistency."),
        ("Termination clause enforceability", "Assess the contractual termination language and whether further legal research is required."),
        ("Bonus and incentive compensation", "Assess compensation allegedly earned during any notice period using verified authorities."),
    ],
    "corporate": [
        ("Change-of-control restrictions", "Identify provisions triggered by an acquisition or change of control."),
        ("Assignment restrictions", "Identify consent or assignment constraints in material agreements."),
        ("Material adverse change", "Review negotiated risk allocation and material adverse change provisions."),
    ],
    "privacy": [
        ("Authority and consent", "Identify the legal and contractual basis for personal information handling."),
        ("Data processing safeguards", "Review processor obligations, security commitments, and transfer controls."),
        ("Incident notification", "Identify contractual and statutory notification obligations for security incidents."),
    ],
}

PRACTICE_GAPS = {
    "employment": [
        "Confirm the signed employment agreement and every amendment relied upon.",
        "Confirm the employer's stated effective termination date against payroll and HR records.",
        "Obtain the governing bonus / incentive compensation plan and any amendments.",
        "Confirm mitigation activity and post-termination compensation, if relevant.",
    ],
    "corporate": [
        "Confirm the complete material-contract schedule and most recent amendments.",
        "Confirm which agreements require consent to assignment or change of control.",
        "Confirm closing conditions, disclosure schedules, and outstanding diligence requests.",
    ],
    "privacy": [
        "Confirm the data-flow inventory and categories of personal information involved.",
        "Confirm current vendor DPAs, subprocessors, and data-location information.",
        "Confirm the incident-response and retention policies applicable to the matter.",
    ],
}


def _practice_key(area: str):
    a = (area or "").lower()
    if "employ" in a: return "employment"
    if any(x in a for x in ["corporate", "m&a", "merger", "acquisition"]): return "corporate"
    if "privacy" in a: return "privacy"
    return "general"


def _parse_date(text: str):
    for pattern in DATE_PATTERNS:
        m = re.search(pattern, text, flags=re.I)
        if not m: continue
        raw = m.group(0)
        for fmt in ["%B %d, %Y", "%Y-%m-%d"]:
            try:
                return datetime.strptime(raw, fmt)
            except ValueError:
                pass
    return None


def _sentences(text: str):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", text or "") if 25 <= len(s.strip()) <= 700]


def _page_for_sentence(db: Session, document_id: int, sentence: str):
    pages = db.query(DocumentPage).filter(DocumentPage.document_id == document_id).order_by(DocumentPage.page_number).all()
    needle = sentence[:80].lower()
    for p in pages:
        if needle and needle in (p.text_content or "").lower():
            return p.page_number
    return 1


def _clear_generated(db: Session, tenant_id: int, matter_id: int):
    for model in [IssueAuthority, EvidenceLink, MatterFact, Claim, LegalIssue, MatterDeadline, MissingInformation, Recommendation]:
        db.query(model).filter(model.tenant_id == tenant_id, model.matter_id == matter_id).delete(synchronize_session=False)
    db.flush()


def build_matter_intelligence(db: Session, tenant_id: int, matter_id: int, reason: str = "manual_refresh"):
    matter = db.query(Matter).filter(Matter.id == matter_id, Matter.tenant_id == tenant_id).first()
    if not matter:
        raise ValueError("Matter not found")
    docs = db.query(Document).filter(Document.tenant_id == tenant_id, Document.matter_id == matter_id).order_by(Document.created_at).all()
    tasks = db.query(Task).filter(Task.tenant_id == tenant_id, Task.matter_id == matter_id).all()
    events = db.query(Event).filter(Event.tenant_id == tenant_id, Event.matter_id == matter_id).all()
    _clear_generated(db, tenant_id, matter_id)

    facts_created = 0
    claim_candidates = []
    dated_by_topic = {}
    claim_keywords = ["terminated", "termination", "notice", "bonus", "agreed", "required", "breach", "consent", "assigned", "renewal", "effective"]

    for doc in docs:
        for sentence in _sentences(doc.text_content or "")[:80]:
            event_date = _parse_date(sentence)
            lowered = sentence.lower()
            page = _page_for_sentence(db, doc.id, sentence)
            if event_date or any(k in lowered for k in ["deadline", "signed", "emailed", "paid", "terminated", "effective"]):
                db.add(MatterFact(
                    tenant_id=tenant_id, matter_id=matter_id, statement=sentence[:1000],
                    fact_type="dated_event" if event_date else "document_fact", event_date=event_date,
                    confidence=.84 if event_date else .72, document_id=doc.id, page_number=page,
                    source_quote=sentence[:700]
                ))
                facts_created += 1
            if any(k in lowered for k in claim_keywords):
                claim_candidates.append((doc, page, sentence))
            topic = None
            if "terminat" in lowered and event_date: topic = "Termination date"
            elif "renew" in lowered and event_date: topic = "Renewal date"
            elif "closing" in lowered and event_date: topic = "Closing date"
            if topic:
                dated_by_topic.setdefault(topic, []).append((doc, page, sentence, event_date))

    claims_created = 0
    contradictions = 0
    used_quotes = set()

    # Create explicit contradiction claims when multiple documents state different dates for the same topic.
    for topic, items in dated_by_topic.items():
        unique_dates = {i[3].date().isoformat() for i in items}
        if len(unique_dates) > 1:
            claim = Claim(tenant_id=tenant_id, matter_id=matter_id, title=topic,
                          statement=f"The record contains inconsistent evidence about the {topic.lower()}.",
                          status="conflict", confidence=.93)
            db.add(claim); db.flush(); claims_created += 1; contradictions += 1
            baseline = items[0][3].date().isoformat()
            for idx, (doc, page, sentence, event_date) in enumerate(items[:6]):
                rel = "supports" if event_date.date().isoformat() == baseline else "contradicts"
                db.add(EvidenceLink(tenant_id=tenant_id, matter_id=matter_id, claim_id=claim.id,
                                    document_id=doc.id, page_number=page, relationship=rel,
                                    quote=sentence[:700], strength=.9, verified=True))
                used_quotes.add(sentence)

    # Turn a limited set of sourced document statements into reviewable claims.
    for doc, page, sentence in claim_candidates:
        if sentence in used_quotes or claims_created >= 8: continue
        short = sentence[:150]
        title = short.split(".")[0][:90]
        claim = Claim(tenant_id=tenant_id, matter_id=matter_id, title=title,
                      statement=sentence[:1000], status="supported", confidence=.76)
        db.add(claim); db.flush(); claims_created += 1
        db.add(EvidenceLink(tenant_id=tenant_id, matter_id=matter_id, claim_id=claim.id,
                            document_id=doc.id, page_number=page, relationship="supports",
                            quote=sentence[:700], strength=.78, verified=True))

    # Ensure every demo matter has at least one reviewable claim.
    if claims_created == 0:
        statement = matter.summary or f"Review the available evidence for {matter.title}."
        claim = Claim(tenant_id=tenant_id, matter_id=matter_id, title="Matter position requiring review",
                      statement=statement, status="needs_review", confidence=.55)
        db.add(claim); db.flush(); claims_created = 1

    # Legal issues and verified corpus mappings.
    key = _practice_key(matter.practice_area)
    issue_defs = PRACTICE_ISSUES.get(key, [("Core legal issues", "Identify the governing legal issues from verified sources and matter facts.")])
    for title, description in issue_defs:
        issue = LegalIssue(tenant_id=tenant_id, matter_id=matter_id, title=title, description=description, confidence=.76)
        db.add(issue); db.flush()
        authorities = retrieve(db, f"{title} {matter.practice_area}", matter.jurisdiction, 3)
        for auth in authorities[:2]:
            db.add(IssueAuthority(tenant_id=tenant_id, matter_id=matter_id, issue_id=issue.id,
                                  corpus_document_id=auth.id,
                                  relevance_note=f"Retrieved from Rafi's authorized corpus for review against: {title}.",
                                  verified=bool((auth.metadata_json or {}).get("verified_case_name_and_citation") or auth.source_type in {"justice_laws", "federal_law"})))

    # Deadlines derived from actual matter/task/event records rather than model guesses.
    seen_deadlines = set()
    if matter.next_deadline:
        db.add(MatterDeadline(tenant_id=tenant_id, matter_id=matter_id, title="Matter next deadline",
                              due_at=matter.next_deadline, source_type="matter", source_id=matter.id, confidence=1.0))
        seen_deadlines.add((matter.next_deadline, "Matter next deadline"))
    for task in tasks:
        if task.due_at and task.status != "done":
            db.add(MatterDeadline(tenant_id=tenant_id, matter_id=matter_id, title=task.title,
                                  due_at=task.due_at, source_type="task", source_id=task.id, confidence=1.0))
    for event in events:
        db.add(MatterDeadline(tenant_id=tenant_id, matter_id=matter_id, title=event.title,
                              due_at=event.start_at, source_type="event", source_id=event.id, confidence=1.0))

    # Gaps are explicit review prompts, not assertions that a document is definitely absent.
    for idx, gap in enumerate(PRACTICE_GAPS.get(key, ["Confirm the complete factual record and identify missing source documents.", "Confirm the governing jurisdiction and procedural posture."])):
        db.add(MissingInformation(tenant_id=tenant_id, matter_id=matter_id, description=gap,
                                  priority="high" if idx < 2 else "medium", requested_from="Client / matter team"))

    # Recommended next actions are workflow suggestions requiring lawyer approval.
    if contradictions:
        db.add(Recommendation(tenant_id=tenant_id, matter_id=matter_id,
                              title="Resolve contradictory source evidence",
                              rationale=f"Rafi detected {contradictions} source conflict(s). Review the cited pages before relying on the disputed fact.",
                              action_type="evidence_review", priority="high"))
    if matter.next_deadline:
        db.add(Recommendation(tenant_id=tenant_id, matter_id=matter_id,
                              title="Confirm upcoming deadline and responsible lawyer",
                              rationale="The matter has an upcoming recorded deadline. Confirm source, calculation, and ownership before reliance.",
                              action_type="deadline_review", priority="high"))
    db.add(Recommendation(tenant_id=tenant_id, matter_id=matter_id,
                          title="Review issue-to-authority mappings",
                          rationale="Rafi retrieved potentially relevant Canadian authorities. Counsel should verify currency, treatment, and applicability.",
                          action_type="research_review", priority="medium"))

    run = IntelligenceRun(tenant_id=tenant_id, matter_id=matter_id, status="completed",
                          documents_scanned=len(docs), facts_created=facts_created,
                          claims_created=claims_created, contradictions_found=contradictions)
    db.add(run)
    digest = MatterDigest(tenant_id=tenant_id, matter_id=matter_id,
                          title="Matter intelligence refreshed",
                          summary=f"Scanned {len(docs)} document(s), extracted {facts_created} source-linked fact(s), built {claims_created} claim(s), and flagged {contradictions} contradiction(s).",
                          change_type=reason)
    db.add(digest)
    matter.updated_at = datetime.utcnow()
    db.commit()
    return run


def intelligence_payload(db: Session, tenant_id: int, matter_id: int):
    matter = db.query(Matter).filter(Matter.id == matter_id, Matter.tenant_id == tenant_id).first()
    if not matter: return None
    docs = {d.id: d for d in db.query(Document).filter(Document.tenant_id == tenant_id, Document.matter_id == matter_id).all()}
    claims = db.query(Claim).filter(Claim.tenant_id == tenant_id, Claim.matter_id == matter_id).all()
    evidence = db.query(EvidenceLink).filter(EvidenceLink.tenant_id == tenant_id, EvidenceLink.matter_id == matter_id).all()
    facts = db.query(MatterFact).filter(MatterFact.tenant_id == tenant_id, MatterFact.matter_id == matter_id).order_by(MatterFact.event_date.asc().nullslast(), MatterFact.id).all()
    issues = db.query(LegalIssue).filter(LegalIssue.tenant_id == tenant_id, LegalIssue.matter_id == matter_id).all()
    authorities = db.query(IssueAuthority).filter(IssueAuthority.tenant_id == tenant_id, IssueAuthority.matter_id == matter_id).all()
    corpus_ids = [a.corpus_document_id for a in authorities]
    corpus = {c.id: c for c in db.query(CorpusDocument).filter(CorpusDocument.id.in_(corpus_ids)).all()} if corpus_ids else {}
    deadlines = db.query(MatterDeadline).filter(MatterDeadline.tenant_id == tenant_id, MatterDeadline.matter_id == matter_id).order_by(MatterDeadline.due_at).all()
    gaps = db.query(MissingInformation).filter(MissingInformation.tenant_id == tenant_id, MissingInformation.matter_id == matter_id).all()
    recs = db.query(Recommendation).filter(Recommendation.tenant_id == tenant_id, Recommendation.matter_id == matter_id).order_by(Recommendation.id.desc()).all()
    digests = db.query(MatterDigest).filter(MatterDigest.tenant_id == tenant_id, MatterDigest.matter_id == matter_id).order_by(MatterDigest.created_at.desc()).limit(10).all()
    runs = db.query(IntelligenceRun).filter(IntelligenceRun.tenant_id == tenant_id, IntelligenceRun.matter_id == matter_id).order_by(IntelligenceRun.created_at.desc()).limit(5).all()

    issue_map = {i.id: i for i in issues}
    nodes = []
    edges = []
    for c in claims:
        nodes.append({"id": f"claim:{c.id}", "type": "claim", "label": c.title, "subtitle": c.status, "confidence": c.confidence})
    for e in evidence:
        d = docs.get(e.document_id)
        nodes.append({"id": f"evidence:{e.id}", "type": "evidence", "label": d.name if d else "Evidence", "subtitle": f"p. {e.page_number} · {e.relationship}", "document_id": e.document_id, "page_number": e.page_number, "quote": e.quote, "relationship": e.relationship})
        edges.append({"source": f"claim:{e.claim_id}", "target": f"evidence:{e.id}", "relation": e.relationship})
    for issue in issues:
        nodes.append({"id": f"issue:{issue.id}", "type": "issue", "label": issue.title, "subtitle": issue.status, "confidence": issue.confidence})
    for a in authorities:
        c = corpus.get(a.corpus_document_id)
        if not c: continue
        nodes.append({"id": f"authority:{a.id}", "type": "authority", "label": c.title, "subtitle": c.citation or c.source_type, "citation": c.citation, "url": c.source_url, "verified": a.verified})
        edges.append({"source": f"issue:{a.issue_id}", "target": f"authority:{a.id}", "relation": "supported_by"})

    # Connect claims to issues heuristically for a useful graph without inventing legal conclusions.
    if issues:
        for idx, claim in enumerate(claims):
            issue = issues[idx % len(issues)]
            edges.append({"source": f"claim:{claim.id}", "target": f"issue:{issue.id}", "relation": "review_against"})

    return {
        "matter": matter,
        "summary": {
            "facts": len(facts), "claims": len(claims), "evidence_links": len(evidence),
            "contradictions": sum(1 for e in evidence if e.relationship == "contradicts"),
            "issues": len(issues), "authorities": len(authorities), "missing": sum(1 for g in gaps if g.status == "open"),
            "deadlines": sum(1 for d in deadlines if d.status == "open"),
        },
        "facts": facts,
        "claims": claims,
        "evidence": [{"id":e.id,"claim_id":e.claim_id,"document_id":e.document_id,"document_name":docs.get(e.document_id).name if docs.get(e.document_id) else "Document","page_number":e.page_number,"relationship":e.relationship,"quote":e.quote,"strength":e.strength,"verified":e.verified} for e in evidence],
        "issues": [{"id":i.id,"title":i.title,"description":i.description,"status":i.status,"confidence":i.confidence,
                    "authorities":[{"id":a.id,"title":corpus[a.corpus_document_id].title,"citation":corpus[a.corpus_document_id].citation,"url":corpus[a.corpus_document_id].source_url,"verified":a.verified,"relevance_note":a.relevance_note} for a in authorities if a.issue_id==i.id and a.corpus_document_id in corpus]} for i in issues],
        "deadlines": deadlines,
        "missing_information": gaps,
        "recommendations": recs,
        "digests": digests,
        "runs": runs,
        "graph": {"nodes": nodes, "edges": edges},
        "guardrails": {"human_review_required": True, "evidence_links_source_backed": True, "authority_applicability_requires_counsel_review": True}
    }
