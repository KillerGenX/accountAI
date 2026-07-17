import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Numeric, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from src.core.database import Base

class SystemBaseModel(Base):
    """
    Abstract Base Model for all system tables.
    Provides standard audit and soft delete fields.
    """
    __abstract__ = True
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()")
    )
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        default=func.now()
    )
    deleted_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

class WorkspaceModel(SystemBaseModel):
    """
    Table representing Multi-Tenant Workspaces (Tenants).
    """
    __tablename__ = "workspaces"

    name = Column(String, nullable=False)
    company_name = Column(String, nullable=True)
    industry = Column(String, nullable=True)
    timezone = Column(String, nullable=False, server_default="Asia/Jakarta", default="Asia/Jakarta")
    currency = Column(String(3), nullable=False, server_default="IDR", default="IDR")
    logo_url = Column(String, nullable=True)
    status = Column(String, nullable=False, server_default="active", default="active")

    # Relationships
    users = relationship("UserModel", back_populates="workspace", cascade="all, delete-orphan")
    employee_configs = relationship("EmployeeConfigModel", back_populates="workspace", cascade="all, delete-orphan")
    settings = relationship("UserSettingsModel", back_populates="workspace", cascade="all, delete-orphan")

class UserModel(SystemBaseModel):
    """
    Table representing users inside a workspace.
    Auth credentials managed by Supabase Auth; this handles profile metadata and roles.
    """
    __tablename__ = "users"

    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    full_name = Column(String, nullable=True)
    role = Column(String, nullable=False)  # administrator, account_manager, sales_manager
    status = Column(String, nullable=False, server_default="pending", default="pending")  # active, inactive, pending
    
    invited_by = Column(UUID(as_uuid=True), nullable=True)
    invited_at = Column(DateTime(timezone=True), nullable=True)
    joined_at = Column(DateTime(timezone=True), nullable=True)
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    workspace = relationship("WorkspaceModel", back_populates="users")
    personal_settings = relationship("UserSettingsModel", back_populates="user", uselist=False, cascade="all, delete-orphan")

class UserSettingsModel(SystemBaseModel):
    """
    Table representing personal configuration preferences per user.
    """
    __tablename__ = "user_settings"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    
    notification_preferences = Column(
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
        default=dict
    )
    display_preferences = Column(
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
        default=dict
    )

    # Relationships
    user = relationship("UserModel", back_populates="personal_settings")
    workspace = relationship("WorkspaceModel", back_populates="settings")

class EmployeeConfigModel(Base):
    """
    Table representing Digital Employee config preferences per workspace.
    No SystemBaseModel hierarchy because it does not require soft deletes.
    """
    __tablename__ = "employee_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()"))
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    employee_name = Column(String, nullable=False)  # e.g., CompanyResearchEmployee
    is_enabled = Column(Boolean, nullable=False, server_default="true", default=True)
    config = Column(
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
        default=dict
    )
    cost_limit_usd = Column(Numeric(10, 2), nullable=True)
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        default=func.now()
    )

    # Relationships
    workspace = relationship("WorkspaceModel", back_populates="employee_configs")
