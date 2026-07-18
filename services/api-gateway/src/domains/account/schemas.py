from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID


# --- Core Account Schemas ---
class AccountBase(BaseModel):
    company_name: str = Field(
        ..., min_length=1, max_length=150, description="Legal company name"
    )
    company_url: Optional[str] = Field(None, description="Website URL of the company")
    industry: Optional[str] = Field(
        None, max_length=100, description="Primary industry sector"
    )
    sub_industry: Optional[str] = Field(
        None, max_length=100, description="Sub-industry sector"
    )
    company_size: Optional[str] = Field(
        None, max_length=50, description="Size category, e.g., Small, Mid, Enterprise"
    )
    employee_count_min: Optional[int] = Field(
        None, ge=0, description="Minimum range of employee count"
    )
    employee_count_max: Optional[int] = Field(
        None, ge=0, description="Maximum range of employee count"
    )
    headquarters: Optional[str] = Field(
        None, max_length=200, description="HQ location address"
    )
    founded_year: Optional[int] = Field(
        None, ge=1700, le=2100, description="Year company was founded"
    )
    assigned_to: Optional[UUID] = Field(
        None, description="User ID of the assigned Account Manager"
    )


class AccountCreate(AccountBase):
    workspace_id: UUID = Field(..., description="Workspace ID this account belongs to")


class AccountResponse(AccountBase):
    id: UUID
    workspace_id: UUID
    business_summary: Optional[str] = None
    completeness_score: int
    status: str
    source: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Contact Schemas ---
class ContactBase(BaseModel):
    full_name: str = Field(
        ..., min_length=1, max_length=100, description="Contact person full name"
    )
    title: Optional[str] = Field(None, max_length=100, description="Job title")
    department: Optional[str] = Field(
        None, max_length=100, description="Job department"
    )
    seniority: Optional[str] = Field(
        None,
        pattern="^(c_level|vp|director|manager|individual)$",
        description="Seniority level classification",
    )
    buying_role: Optional[str] = Field(
        None,
        pattern="^(decision_maker|influencer|evaluator|procurement)$",
        description="Buying process role",
    )
    linkedin_url: Optional[str] = Field(None, description="LinkedIn profile URL")
    email: Optional[str] = Field(None, description="Work email address")
    phone: Optional[str] = Field(None, description="Contact phone number")
    is_primary: bool = Field(
        False, description="Whether this is the primary account contact"
    )


class ContactCreate(ContactBase):
    pass


class ContactResponse(ContactBase):
    id: UUID
    workspace_id: UUID
    account_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Intelligence Records Schemas ---
class IntelligenceResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    account_id: UUID
    intel_type: str
    content: str
    source_url: Optional[str] = None
    confidence: Optional[float] = None
    generated_by: str
    valid_until: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- News Schemas ---
class NewsResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    account_id: UUID
    headline: str
    summary: Optional[str] = None
    source_url: Optional[str] = None
    published_at: Optional[datetime] = None
    signal_type: Optional[str] = None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Notes Schemas ---
class NoteCreate(BaseModel):
    user_id: UUID = Field(..., description="User ID writing the note")
    content: str = Field(..., min_length=1, description="Private note content text")


class NoteResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    account_id: UUID
    user_id: UUID
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Document & RAG Schemas ---
class DocumentResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    account_id: UUID
    filename: str
    file_size: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RagQueryRequest(BaseModel):
    account_id: UUID
    query: str = Field(
        ...,
        min_length=1,
        description="Question about the account capabilities or internal documents",
    )


class RagCitation(BaseModel):
    source_name: str
    source_type: str  # "document" or "note"


class RagQueryResponse(BaseModel):
    answer: str
    citations: List[RagCitation]
