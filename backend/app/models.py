from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, Boolean, Integer, JSON, Float
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base


class Tenant(Base):
    __tablename__ = "tenants"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), default="Rafi Demo Firm")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(200), default="Demo Counsel")
    role: Mapped[str] = mapped_column(String(50), default="admin")
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class Client(Base):
    __tablename__ = "clients"
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(index=True)
    name: Mapped[str] = mapped_column(String(200), index=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(100), nullable=True)
    company: Mapped[str | None] = mapped_column(String(200), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Matter(Base):
    __tablename__ = "matters"
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(index=True)
    client_id: Mapped[int | None] = mapped_column(ForeignKey("clients.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    matter_number: Mapped[str] = mapped_column(String(100), index=True)
    practice_area: Mapped[str] = mapped_column(String(120), default="General")
    jurisdiction: Mapped[str] = mapped_column(String(120), default="Ontario, Canada")
    stage: Mapped[str] = mapped_column(String(100), default="Intake")
    status: Mapped[str] = mapped_column(String(50), default="active")
    opposing_party: Mapped[str | None] = mapped_column(String(200), nullable=True)
    opposing_counsel: Mapped[str | None] = mapped_column(String(200), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    risk_score: Mapped[float] = mapped_column(Float, default=0.25)
    next_deadline: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Document(Base):
    __tablename__ = "documents"
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(index=True)
    matter_id: Mapped[int | None] = mapped_column(ForeignKey("matters.id"), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    category: Mapped[str] = mapped_column(String(100), default="General")
    path: Mapped[str | None] = mapped_column(String(600), nullable=True)
    text_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="uploaded")
    version: Mapped[int] = mapped_column(Integer, default=1)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class DocumentPage(Base):
    __tablename__ = "document_pages"
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(index=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), index=True)
    page_number: Mapped[int] = mapped_column(Integer, default=1)
    text_content: Mapped[str] = mapped_column(Text, default="")


class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(index=True)
    matter_id: Mapped[int | None] = mapped_column(ForeignKey("matters.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(60), default="todo")
    priority: Mapped[str] = mapped_column(String(30), default="medium")
    due_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    assigned_to: Mapped[str | None] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Event(Base):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(index=True)
    matter_id: Mapped[int | None] = mapped_column(ForeignKey("matters.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(255))
    start_at: Mapped[datetime] = mapped_column(DateTime)
    end_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source: Mapped[str] = mapped_column(String(50), default="rafi")


class TeamNote(Base):
    __tablename__ = "team_notes"
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(index=True)
    matter_id: Mapped[int | None] = mapped_column(ForeignKey("matters.id"), nullable=True)
    author: Mapped[str] = mapped_column(String(200))
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Message(Base):
    __tablename__ = "messages"
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(index=True)
    matter_id: Mapped[int | None] = mapped_column(ForeignKey("matters.id"), nullable=True)
    sender: Mapped[str] = mapped_column(String(200))
    recipient: Mapped[str] = mapped_column(String(200))
    body: Mapped[str] = mapped_column(Text)
    client_visible: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class SignatureRequest(Base):
    __tablename__ = "signature_requests"
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(index=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"))
    signer_email: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(60), default="sent")
    signed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class Workflow(Base):
    __tablename__ = "workflows"
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(index=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, default="")
    steps: Mapped[list] = mapped_column(JSON, default=list)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    runs: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class FirmPlaybook(Base):
    __tablename__ = "firm_playbooks"
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(index=True)
    name: Mapped[str] = mapped_column(String(200))
    practice_area: Mapped[str] = mapped_column(String(120), default="General")
    description: Mapped[str] = mapped_column(Text, default="")
    rules: Mapped[list] = mapped_column(JSON, default=list)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ResearchItem(Base):
    __tablename__ = "research_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(index=True)
    query: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text)
    sources: Mapped[list] = mapped_column(JSON, default=list)
    jurisdiction: Mapped[str] = mapped_column(String(120), default="Canada")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class CorpusDocument(Base):
    __tablename__ = "corpus_documents"
    id: Mapped[int] = mapped_column(primary_key=True)
    source_type: Mapped[str] = mapped_column(String(80), index=True)
    title: Mapped[str] = mapped_column(String(400), index=True)
    citation: Mapped[str | None] = mapped_column(String(250), nullable=True, index=True)
    jurisdiction: Mapped[str] = mapped_column(String(120), default="Canada")
    source_url: Mapped[str | None] = mapped_column(String(800), nullable=True)
    current_to: Mapped[str | None] = mapped_column(String(80), nullable=True)
    text_content: Mapped[str] = mapped_column(Text)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# --- Rafi v2 Matter Intelligence Graph ---
class MatterFact(Base):
    __tablename__ = "matter_facts"
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(index=True)
    matter_id: Mapped[int] = mapped_column(ForeignKey("matters.id"), index=True)
    statement: Mapped[str] = mapped_column(Text)
    fact_type: Mapped[str] = mapped_column(String(80), default="event")
    event_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.75)
    status: Mapped[str] = mapped_column(String(40), default="extracted")
    document_id: Mapped[int | None] = mapped_column(ForeignKey("documents.id"), nullable=True)
    page_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source_quote: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Claim(Base):
    __tablename__ = "claims"
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(index=True)
    matter_id: Mapped[int] = mapped_column(ForeignKey("matters.id"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    statement: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(60), default="needs_review")
    confidence: Mapped[float] = mapped_column(Float, default=0.65)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class EvidenceLink(Base):
    __tablename__ = "evidence_links"
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(index=True)
    matter_id: Mapped[int] = mapped_column(ForeignKey("matters.id"), index=True)
    claim_id: Mapped[int] = mapped_column(ForeignKey("claims.id"), index=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), index=True)
    page_number: Mapped[int] = mapped_column(Integer, default=1)
    relationship: Mapped[str] = mapped_column(String(40), default="supports")
    quote: Mapped[str] = mapped_column(Text, default="")
    strength: Mapped[float] = mapped_column(Float, default=0.7)
    verified: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class LegalIssue(Base):
    __tablename__ = "legal_issues"
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(index=True)
    matter_id: Mapped[int] = mapped_column(ForeignKey("matters.id"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(50), default="open")
    confidence: Mapped[float] = mapped_column(Float, default=0.7)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class IssueAuthority(Base):
    __tablename__ = "issue_authorities"
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(index=True)
    matter_id: Mapped[int] = mapped_column(ForeignKey("matters.id"), index=True)
    issue_id: Mapped[int] = mapped_column(ForeignKey("legal_issues.id"), index=True)
    corpus_document_id: Mapped[int] = mapped_column(ForeignKey("corpus_documents.id"), index=True)
    relevance_note: Mapped[str] = mapped_column(Text, default="")
    verified: Mapped[bool] = mapped_column(Boolean, default=True)


class MatterDeadline(Base):
    __tablename__ = "matter_deadlines"
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(index=True)
    matter_id: Mapped[int] = mapped_column(ForeignKey("matters.id"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    due_at: Mapped[datetime] = mapped_column(DateTime)
    source_type: Mapped[str] = mapped_column(String(60), default="matter")
    source_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="open")
    confidence: Mapped[float] = mapped_column(Float, default=0.9)


class MissingInformation(Base):
    __tablename__ = "missing_information"
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(index=True)
    matter_id: Mapped[int] = mapped_column(ForeignKey("matters.id"), index=True)
    description: Mapped[str] = mapped_column(Text)
    priority: Mapped[str] = mapped_column(String(30), default="medium")
    status: Mapped[str] = mapped_column(String(40), default="open")
    requested_from: Mapped[str | None] = mapped_column(String(200), nullable=True)


class Recommendation(Base):
    __tablename__ = "recommendations"
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(index=True)
    matter_id: Mapped[int] = mapped_column(ForeignKey("matters.id"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    rationale: Mapped[str] = mapped_column(Text, default="")
    action_type: Mapped[str] = mapped_column(String(80), default="review")
    priority: Mapped[str] = mapped_column(String(30), default="medium")
    status: Mapped[str] = mapped_column(String(40), default="proposed")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class MatterDigest(Base):
    __tablename__ = "matter_digests"
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(index=True)
    matter_id: Mapped[int] = mapped_column(ForeignKey("matters.id"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    summary: Mapped[str] = mapped_column(Text)
    change_type: Mapped[str] = mapped_column(String(60), default="intelligence_refresh")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class IntelligenceRun(Base):
    __tablename__ = "intelligence_runs"
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(index=True)
    matter_id: Mapped[int] = mapped_column(ForeignKey("matters.id"), index=True)
    status: Mapped[str] = mapped_column(String(40), default="completed")
    documents_scanned: Mapped[int] = mapped_column(Integer, default=0)
    facts_created: Mapped[int] = mapped_column(Integer, default=0)
    claims_created: Mapped[int] = mapped_column(Integer, default=0)
    contradictions_found: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

# --- Rafi v3 public growth / early-access CRM ---
class WaitlistLead(Base):
    __tablename__ = "waitlist_leads"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    organization: Mapped[str | None] = mapped_column(String(240), nullable=True)
    role: Mapped[str | None] = mapped_column(String(160), nullable=True)
    team_size: Mapped[str | None] = mapped_column(String(80), nullable=True)
    country: Mapped[str | None] = mapped_column(String(120), nullable=True)
    referral: Mapped[str | None] = mapped_column(String(240), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="new")
    source: Mapped[str] = mapped_column(String(80), default="website")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class DemoRequest(Base):
    __tablename__ = "demo_requests"
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(120))
    last_name: Mapped[str] = mapped_column(String(120))
    work_email: Mapped[str] = mapped_column(String(255), index=True)
    organization: Mapped[str] = mapped_column(String(240))
    role: Mapped[str | None] = mapped_column(String(160), nullable=True)
    team_size: Mapped[str | None] = mapped_column(String(80), nullable=True)
    practice_area: Mapped[str | None] = mapped_column(String(160), nullable=True)
    country: Mapped[str | None] = mapped_column(String(120), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(80), nullable=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="new")
    source: Mapped[str] = mapped_column(String(80), default="website")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
