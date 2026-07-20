import uuid
from sqlalchemy import Column, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from src.core.database import Base


class Prospect(Base):
    __tablename__ = "prospects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), nullable=False)
    company_name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    match_reason = Column(Text, nullable=True)
    source_url = Column(Text, nullable=True)
    status = Column(Text, nullable=False, default="pending")
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)
