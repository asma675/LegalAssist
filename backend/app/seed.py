from datetime import datetime, timedelta
from urllib.parse import quote_plus
from sqlalchemy.orm import Session
from .models import (
    Tenant, User, Client, Matter, Task, Event, TeamNote, Workflow, CorpusDocument,
    Document, DocumentPage, FirmPlaybook
)
from .auth import hash_password

REAL_CASE_NOTES = [
    ("R. v. Oakes", "[1986] 1 S.C.R. 103", "Canada", "Leading Supreme Court of Canada authority establishing the structured section 1 proportionality analysis commonly called the Oakes test."),
    ("Bhasin v. Hrynew", "2014 SCC 71", "Canada", "Recognized good faith as an organizing principle of Canadian contract law and a duty of honest performance."),
    ("Hryniak v. Mauldin", "2014 SCC 7", "Ontario / Canada", "Leading authority encouraging proportionate, timely and affordable adjudication and a broader approach to summary judgment."),
    ("Canada (Minister of Citizenship and Immigration) v. Vavilov", "2019 SCC 65", "Canada", "Leading administrative-law authority on the framework for judicial review of administrative decisions."),
    ("Carter v. Canada (Attorney General)", "2015 SCC 5", "Canada", "Supreme Court of Canada Charter decision concerning the prohibition on medical assistance in dying."),
    ("R. v. Jordan", "2016 SCC 27", "Canada", "Established presumptive ceilings for unreasonable delay analysis under section 11(b) of the Charter."),
    ("Uber Technologies Inc. v. Heller", "2020 SCC 16", "Ontario / Canada", "Addressed unconscionability, arbitration clauses, and access to justice in a standard-form contract."),
    ("Matthews v. Ocean Nutrition Canada Ltd.", "2020 SCC 26", "Canada", "Clarified the analysis for wrongful-dismissal damages and incentive compensation during the reasonable notice period."),
    ("Potter v. New Brunswick Legal Aid Services Commission", "2015 SCC 10", "Canada", "Leading authority on constructive dismissal, including an employer's suspension of an employee."),
    ("Haaretz.com v. Goldhar", "2018 SCC 28", "Ontario / Canada", "Addressed jurisdiction and forum non conveniens in an internet defamation dispute."),
    ("C.M. Callow Inc. v. Zollinger", "2020 SCC 45", "Ontario / Canada", "Applied the duty of honest performance and addressed knowingly misleading contractual conduct."),
    ("Wastech Services Ltd. v. Greater Vancouver Sewerage and Drainage District", "2021 SCC 7", "Canada", "Considered the duty to exercise contractual discretion in good faith."),
    ("Honda Canada Inc. v. Keays", "2008 SCC 39", "Ontario / Canada", "Leading employment decision addressing damages arising from the manner of dismissal and the principles governing such awards."),
    ("Machtinger v. HOJ Industries Ltd.", "[1992] 1 S.C.R. 986", "Ontario / Canada", "Leading authority on the consequences of employment termination clauses that fail to comply with minimum employment standards."),
    ("Wilson v. Atomic Energy of Canada Ltd.", "2016 SCC 29", "Canada", "Addressed unjust dismissal under the Canada Labour Code for non-unionized federal employees."),
]

FEDERAL_REFERENCE_NOTES = [
    ("Personal Information Protection and Electronic Documents Act", "S.C. 2000, c. 5", "Canada", "Federal private-sector privacy legislation. Verify current application, amendments, and provincial-equivalency issues before relying on this summary.", "https://laws-lois.justice.gc.ca/eng/acts/P-8.6/"),
    ("Canada Labour Code", "R.S.C., 1985, c. L-2", "Canada", "Federal labour and employment statute applying within federal jurisdiction. Verify the relevant Part and current consolidated text.", "https://laws-lois.justice.gc.ca/eng/acts/L-2/"),
    ("Competition Act", "R.S.C., 1985, c. C-34", "Canada", "Federal competition statute. Verify current provisions and enforcement guidance for the issue under review.", "https://laws-lois.justice.gc.ca/eng/acts/C-34/"),
    ("Canada Business Corporations Act", "R.S.C., 1985, c. C-44", "Canada", "Federal corporate statute for corporations incorporated under the CBCA. Verify current consolidated provisions before reliance.", "https://laws-lois.justice.gc.ca/eng/acts/C-44/"),
]


def _scc_search(citation: str):
    return f"https://decisions.scc-csc.ca/scc-csc/en/d/s/index.do?cont={quote_plus(citation)}"


def seed(db: Session):
    # Upgrade the original demo credential in-place so v1 Docker volumes remain usable.
    existing_user = db.query(User).filter(User.email == "admin@rafi.local").first()
    if existing_user:
        existing_user.email = "admin@rafi.app"
        db.commit()

    if db.query(Tenant).first():
        # Upgrade an existing v1 demo database in place: add v2 playbooks and build intelligence for existing matters.
        tenant = db.query(Tenant).first()
        if tenant and not db.query(FirmPlaybook).filter(FirmPlaybook.tenant_id == tenant.id).first():
            db.add_all(_playbooks(tenant.id)); db.commit()
        if tenant:
            from .models import IntelligenceRun
            from .intelligence import build_matter_intelligence
            for matter in db.query(Matter).filter(Matter.tenant_id == tenant.id).all():
                if not db.query(IntelligenceRun).filter(IntelligenceRun.tenant_id == tenant.id, IntelligenceRun.matter_id == matter.id).first():
                    build_matter_intelligence(db, tenant.id, matter.id, reason="v2_upgrade")
        return

    tenant = Tenant(name="Whitford & Lane Demo")
    db.add(tenant); db.flush()
    user = User(tenant_id=tenant.id, email="admin@rafi.app", password_hash=hash_password("ChangeMe123!"), full_name="Maya Sterling", role="admin")
    db.add(user)

    clients = [
        Client(tenant_id=tenant.id, name="Acme Manufacturing Ltd.", email="legal@acme.example", company="Acme Manufacturing"),
        Client(tenant_id=tenant.id, name="Jordan Patel", email="jordan.patel@example.com"),
        Client(tenant_id=tenant.id, name="Northstar Health Inc.", email="counsel@northstar.example", company="Northstar Health"),
    ]
    db.add_all(clients); db.flush()

    matters = [
        Matter(tenant_id=tenant.id, client_id=clients[0].id, title="Acme Acquisition", matter_number="M-2026-041", practice_area="Corporate / M&A", stage="Due diligence", summary="Acquisition diligence and transaction document review.", risk_score=.34, next_deadline=datetime.utcnow()+timedelta(days=9)),
        Matter(tenant_id=tenant.id, client_id=clients[1].id, title="Patel Employment Matter", matter_number="M-2026-057", practice_area="Employment", stage="Pre-litigation", summary="Employment termination and compensation review involving disputed termination timing and incentive compensation.", risk_score=.68, next_deadline=datetime.utcnow()+timedelta(days=4)),
        Matter(tenant_id=tenant.id, client_id=clients[2].id, title="Northstar Privacy Review", matter_number="M-2026-063", practice_area="Privacy", stage="Assessment", summary="Privacy compliance assessment and vendor contract remediation.", risk_score=.43, next_deadline=datetime.utcnow()+timedelta(days=14)),
    ]
    db.add_all(matters); db.flush()

    db.add_all([
        Task(tenant_id=tenant.id, matter_id=matters[0].id, title="Review change-of-control clauses", priority="high", due_at=datetime.utcnow()+timedelta(days=2), assigned_to="Maya Sterling"),
        Task(tenant_id=tenant.id, matter_id=matters[1].id, title="Prepare chronology from client records", priority="high", due_at=datetime.utcnow()+timedelta(days=1), assigned_to="Maya Sterling"),
        Task(tenant_id=tenant.id, matter_id=matters[2].id, title="Compare DPA against privacy playbook", priority="medium", due_at=datetime.utcnow()+timedelta(days=5), assigned_to="Alex Chen"),
    ])
    db.add_all([
        Event(tenant_id=tenant.id, matter_id=matters[0].id, title="Acme diligence call", start_at=datetime.utcnow()+timedelta(days=1, hours=3)),
        Event(tenant_id=tenant.id, matter_id=matters[1].id, title="Patel client conference", start_at=datetime.utcnow()+timedelta(days=2, hours=1)),
    ])
    db.add(TeamNote(tenant_id=tenant.id, matter_id=matters[0].id, author="Maya Sterling", body="Prioritize assignment, change-of-control, and material adverse change provisions."))

    db.add_all([
        Workflow(tenant_id=tenant.id, name="New employment matter", description="From intake through conflict check, chronology, gaps, research, and lawyer approval.", steps=["Conflict check", "Create matter", "Request core documents", "Extract facts and dates", "Build intelligence graph", "Run Canadian research", "Draft client questions", "Lawyer approval"]),
        Workflow(tenant_id=tenant.id, name="Contract first-pass review", description="Extract key clauses, compare to playbook, and create an issue list.", steps=["Classify contract", "Extract clauses", "Compare playbook", "Draft issue list", "Human review"]),
        Workflow(tenant_id=tenant.id, name="Litigation chronology", description="Build an evidence-linked chronology from a matter vault.", steps=["Find dated events", "Normalize actors", "Link evidence", "Flag conflicts", "Human review"]),
        Workflow(tenant_id=tenant.id, name="Client update draft", description="Draft a source-linked status update from matter activity.", steps=["Summarize changes", "Check deadlines", "Draft update", "Lawyer approval"]),
    ])
    db.add_all(_playbooks(tenant.id))

    # Curated real Canadian authorities. The case notes are editorial summaries, not copies of case text.
    for title, citation, jurisdiction, note in REAL_CASE_NOTES:
        db.add(CorpusDocument(source_type="case_note", title=title, citation=citation, jurisdiction=jurisdiction,
                              source_url=_scc_search(citation), current_to="2026-09-14", text_content=note,
                              metadata_json={"verified_case_name_and_citation": True, "note_type": "editorial summary", "source_family": "Supreme Court of Canada"}))
    for title, citation, jurisdiction, note, url in FEDERAL_REFERENCE_NOTES:
        db.add(CorpusDocument(source_type="federal_law", title=title, citation=citation, jurisdiction=jurisdiction,
                              source_url=url, current_to="2026-09-14", text_content=note,
                              metadata_json={"official_source": True, "note_type": "reference summary", "source_family": "Justice Laws Website"}))
    db.flush()

    # Demo matter evidence used to demonstrate source-linked claims and contradiction detection.
    termination_letter = Document(tenant_id=tenant.id, matter_id=matters[1].id, name="Termination Letter.pdf", category="Evidence",
                                  text_content="Termination Letter. This letter confirms that Jordan Patel's employment is terminated effective March 3, 2026. The company states that bonus eligibility will be determined under the written incentive plan. Please return company property by March 10, 2026.",
                                  metadata_json={"demo": True, "pages": 1})
    hr_record = Document(tenant_id=tenant.id, matter_id=matters[1].id, name="HR Status Record.pdf", category="Evidence",
                         text_content="HR Status Record. The HR system lists Jordan Patel's termination effective March 7, 2026. Final payroll processing is scheduled after the status change. This record was exported March 8, 2026.",
                         metadata_json={"demo": True, "pages": 1})
    manager_email = Document(tenant_id=tenant.id, matter_id=matters[1].id, name="Manager Email.txt", category="Correspondence",
                             text_content="Manager email dated March 5, 2026. We told Jordan that work had ended, but payroll and access may remain active while HR completes the termination process. Please confirm which date Legal wants treated as effective.",
                             metadata_json={"demo": True, "pages": 1})
    bonus_plan = Document(tenant_id=tenant.id, matter_id=matters[1].id, name="2026 Bonus Plan.txt", category="Compensation",
                          text_content="2026 Bonus Plan. Bonus payment is subject to the written plan terms and specified eligibility conditions. Counsel should review the complete signed plan and any amendments before reaching a conclusion about entitlement.",
                          metadata_json={"demo": True, "pages": 1})
    db.add_all([termination_letter, hr_record, manager_email, bonus_plan]); db.flush()
    for doc in [termination_letter, hr_record, manager_email, bonus_plan]:
        db.add(DocumentPage(tenant_id=tenant.id, document_id=doc.id, page_number=1, text_content=doc.text_content or ""))
    db.commit()

    # Build a working graph immediately so the first login demonstrates v2 without an AI key.
    from .intelligence import build_matter_intelligence
    for matter in matters:
        build_matter_intelligence(db, tenant.id, matter.id, reason="initial_seed")


def _playbooks(tenant_id: int):
    return [
        FirmPlaybook(tenant_id=tenant_id, name="Ontario Employment Matter Playbook", practice_area="Employment",
                     description="Firm review rules for employment intake, termination records, compensation, and lawyer approval.",
                     rules=["Do not state an effective termination date if source records conflict.", "Require the signed employment agreement before clause analysis.", "Require the complete bonus/incentive plan before final compensation analysis.", "Every consequential conclusion must link to evidence and verified authority."]),
        FirmPlaybook(tenant_id=tenant_id, name="M&A Diligence Playbook", practice_area="Corporate / M&A",
                     description="Material-contract review priorities for small and mid-market acquisitions.",
                     rules=["Flag assignment and change-of-control provisions.", "Track required third-party consents.", "Separate extracted contract language from legal interpretation.", "Escalate missing schedules and amendments."]),
        FirmPlaybook(tenant_id=tenant_id, name="Canadian Privacy Review Playbook", practice_area="Privacy",
                     description="Evidence and review checklist for privacy/vendor assessments.",
                     rules=["Identify data categories and processing purposes.", "Track subprocessors and data locations.", "Flag missing incident-notification language.", "Verify governing law from an official or authorized source."]),
    ]
