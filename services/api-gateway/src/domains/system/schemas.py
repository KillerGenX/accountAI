from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class WorkspaceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Name of the workspace/tenant")
    company_name: Optional[str] = Field(None, max_length=100, description="Legal company name associated with workspace")
    industry: Optional[str] = Field(None, max_length=100, description="Industry sector of the company")
    timezone: str = Field("Asia/Jakarta", description="Timezone for the workspace scheduler")
    currency: str = Field("IDR", max_length=3, description="Default currency code (e.g., IDR, USD)")

class WorkspaceCreate(WorkspaceBase):
    pass

class WorkspaceResponse(WorkspaceBase):
    id: UUID
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserBase(BaseModel):
    email: EmailStr = Field(..., description="Unique user email address")
    full_name: Optional[str] = Field(None, max_length=100, description="User's full name")
    role: str = Field(..., pattern="^(administrator|account_manager|sales_manager)$", description="User role in workspace")

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: UUID
    workspace_id: UUID
    status: str
    invited_by: Optional[UUID] = None
    invited_at: Optional[datetime] = None
    joined_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class EmployeeConfigResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    employee_name: str
    is_enabled: bool
    config: dict
    cost_limit_usd: Optional[float] = None
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
