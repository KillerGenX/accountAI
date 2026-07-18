import uuid
from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    Boolean,
    ForeignKey,
    Numeric,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector

from src.core.database import Base


class AccountModel(Base):
    """
    Table representing Core Account Records (Companies).
    """

    __tablename__ = "accounts"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    workspace_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )

    company_name = Column(String, nullable=False)
    company_url = Column(String, nullable=True)
    industry = Column(String, nullable=True)
    sub_industry = Column(String, nullable=True)
    company_size = Column(String, nullable=True)  # small/mid/large/enterprise
    employee_count_min = Column(Integer, nullable=True)
    employee_count_max = Column(Integer, nullable=True)
    headquarters = Column(String, nullable=True)
    founded_year = Column(Integer, nullable=True)
    business_summary = Column(Text, nullable=True)  # AI-generated
    completeness_score = Column(
        Integer, nullable=False, server_default="0", default=0
    )  # 0-100
    status = Column(
        String, nullable=False, server_default="active", default="active"
    )  # active, inactive, archived
    assigned_to = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    source = Column(
        String, nullable=False, server_default="manual", default="manual"
    )  # discovery, manual

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=func.now(),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        default=func.now(),
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Soft delete

    # Relationships
    contacts = relationship(
        "ContactModel", back_populates="account", cascade="all, delete-orphan"
    )
    intelligence = relationship(
        "AccountIntelligenceModel",
        back_populates="account",
        cascade="all, delete-orphan",
    )
    news = relationship(
        "AccountNewsModel", back_populates="account", cascade="all, delete-orphan"
    )
    notes = relationship(
        "AccountNoteModel", back_populates="account", cascade="all, delete-orphan"
    )
    embeddings = relationship(
        "AccountEmbeddingModel", back_populates="account", cascade="all, delete-orphan"
    )


class ContactModel(Base):
    """
    Table representing Contacts and Decision Makers for accounts.
    """

    __tablename__ = "contacts"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    workspace_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    account_id = Column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
    )

    full_name = Column(String, nullable=False)
    title = Column(String, nullable=True)
    department = Column(String, nullable=True)
    seniority = Column(
        String, nullable=True
    )  # c_level, vp, director, manager, individual
    buying_role = Column(
        String, nullable=True
    )  # decision_maker, influencer, evaluator, procurement
    linkedin_url = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    is_primary = Column(Boolean, nullable=False, server_default="false", default=False)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=func.now(),
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Soft delete

    # Relationships
    account = relationship("AccountModel", back_populates="contacts")


class AccountIntelligenceModel(Base):
    """
    Table representing AI-generated Intelligence summaries and context.
    """

    __tablename__ = "account_intelligence"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    workspace_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    account_id = Column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
    )

    intel_type = Column(
        String, nullable=False
    )  # summary, news, industry, technology, financial
    content = Column(Text, nullable=False)
    source_url = Column(String, nullable=True)
    confidence = Column(Numeric(3, 2), nullable=True)
    generated_by = Column(String, nullable=False)  # e.g., CompanyResearchEmployee
    valid_until = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=func.now(),
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Soft delete

    # Relationships
    account = relationship("AccountModel", back_populates="intelligence")


class AccountNewsModel(Base):
    """
    Table representing News alerts and feed for accounts.
    """

    __tablename__ = "account_news"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    workspace_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    account_id = Column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
    )

    headline = Column(String, nullable=False)
    summary = Column(Text, nullable=True)  # AI-summarized
    source_url = Column(String, nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    signal_type = Column(
        String, nullable=True
    )  # e.g., expansion, leadership, financial, technology
    status = Column(
        String,
        nullable=False,
        server_default="pending",
        default="pending",
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=func.now(),
    )

    # Relationships
    account = relationship("AccountModel", back_populates="news")


class AccountNoteModel(Base):
    """
    Table representing AM's Private Notes (Knowledge Layer 3).
    """

    __tablename__ = "account_notes"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    workspace_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    account_id = Column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )  # Private to this user

    content = Column(Text, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=func.now(),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        default=func.now(),
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Soft delete

    # Relationships
    account = relationship("AccountModel", back_populates="notes")


class AccountEmbeddingModel(Base):
    """
    Table representing vector embeddings for semantic search (pgvector).
    """

    __tablename__ = "account_embeddings"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    account_id = Column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
    )

    content_type = Column(String, nullable=False)  # summary, news, contact
    embedding = Column(Vector(1536), nullable=False)  # OpenAI Ada-002 dimensions
    source_record_id = Column(
        UUID(as_uuid=True), nullable=False
    )  # links to source contact/news/intel record
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=func.now(),
    )

    # Relationships
    account = relationship("AccountModel", back_populates="embeddings")
