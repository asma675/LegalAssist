from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserOut(ORMModel):
    id: int
    email: str
    full_name: str
    role: str

class AuthOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

class ClientIn(BaseModel):
    name: str
    email: str | None = None
    phone: str | None = None
    company: str | None = None
    notes: str | None = None

class MatterIn(BaseModel):
    title: str
    matter_number: str
    client_id: int | None = None
    practice_area: str = "General"
    jurisdiction: str = "Ontario, Canada"
    stage: str = "Intake"
    status: str = "active"
    opposing_party: str | None = None
    opposing_counsel: str | None = None
    summary: str | None = None
    next_deadline: datetime | None = None

class TaskIn(BaseModel):
    title: str
    matter_id: int | None = None
    status: str = "todo"
    priority: str = "medium"
    due_at: datetime | None = None
    assigned_to: str | None = None

class EventIn(BaseModel):
    title: str
    matter_id: int | None = None
    start_at: datetime
    end_at: datetime | None = None
    location: str | None = None

class NoteIn(BaseModel):
    matter_id: int | None = None
    body: str

class MessageIn(BaseModel):
    matter_id: int | None = None
    recipient: str
    body: str
    client_visible: bool = True

class WorkflowIn(BaseModel):
    name: str
    description: str = ""
    steps: list = Field(default_factory=list)

class PlaybookIn(BaseModel):
    name: str
    practice_area: str = "General"
    description: str = ""
    rules: list[str] = Field(default_factory=list)

class ChatIn(BaseModel):
    message: str
    matter_id: int | None = None
    jurisdiction: str = "Ontario, Canada"

class ResearchIn(BaseModel):
    query: str
    jurisdiction: str = "Canada"
    top_k: int = 8

class ContractReviewIn(BaseModel):
    text: str
    playbook: str | None = None
    playbook_id: int | None = None
    jurisdiction: str = "Ontario, Canada"

class DraftIn(BaseModel):
    document_type: str
    facts: str
    jurisdiction: str = "Ontario, Canada"
    matter_id: int | None = None
    instructions: str | None = None

class AnalyzeDocumentIn(BaseModel):
    text: str
    analysis_type: str = "issue_spotting"
    jurisdiction: str = "Ontario, Canada"

class SignatureIn(BaseModel):
    document_id: int
    signer_email: EmailStr

class RecommendationStatusIn(BaseModel):
    status: str

class MissingInfoStatusIn(BaseModel):
    status: str

class WaitlistIn(BaseModel):
    email: EmailStr
    full_name: str | None = Field(default=None, max_length=200)
    organization: str | None = Field(default=None, max_length=240)
    role: str | None = Field(default=None, max_length=160)
    team_size: str | None = Field(default=None, max_length=80)
    country: str | None = Field(default="Canada", max_length=120)
    referral: str | None = Field(default=None, max_length=240)
    website: str | None = Field(default=None, max_length=200)  # honeypot

class DemoRequestIn(BaseModel):
    first_name: str = Field(min_length=1, max_length=120)
    last_name: str = Field(min_length=1, max_length=120)
    work_email: EmailStr
    organization: str = Field(min_length=1, max_length=240)
    role: str | None = Field(default=None, max_length=160)
    team_size: str | None = Field(default=None, max_length=80)
    practice_area: str | None = Field(default=None, max_length=160)
    country: str | None = Field(default="Canada", max_length=120)
    phone: str | None = Field(default=None, max_length=80)
    message: str | None = Field(default=None, max_length=3000)
    website: str | None = Field(default=None, max_length=200)  # honeypot
