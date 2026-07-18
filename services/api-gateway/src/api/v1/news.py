from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
import structlog
from uuid import UUID
from typing import List, Optional
from pydantic import BaseModel, Field

from src.core.database import get_db
from src.domains.account.models import AccountNewsModel
from src.domains.account.schemas import NewsResponse
from src.core.auth import get_current_user

logger = structlog.get_logger()
router = APIRouter(tags=["News"])


class StatusUpdate(BaseModel):
    status: str = Field(..., description="New status (pending, approved, rejected)")


@router.get("/", response_model=List[NewsResponse])
async def list_news(
    status_filter: Optional[str] = Query(
        None,
        alias="status",
        description="Filter by status (pending, approved, rejected)",
    ),
    account_id: Optional[UUID] = Query(
        None, description="Filter by corporate account ID"
    ),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Retrieves corporate news signals and alerts, filtered by status or account ID.
    Enforces tenant isolation by always scoping requests to the user's workspace.
    """
    workspace_id = UUID(current_user["workspace_id"])
    await logger.ainfo(
        "list_news_requested",
        workspace_id=str(workspace_id),
        status_filter=status_filter,
        account_id=str(account_id) if account_id else None,
    )

    # Base query filtered by user's workspace
    query = select(AccountNewsModel).where(
        AccountNewsModel.workspace_id == workspace_id
    )

    # Optional status filter
    if status_filter:
        query = query.where(AccountNewsModel.status == status_filter.lower())

    # Optional account ID filter
    if account_id:
        query = query.where(AccountNewsModel.account_id == account_id)

    # Order by newest first
    query = query.order_by(desc(AccountNewsModel.created_at))

    result = await db.execute(query)
    news_items = result.scalars().all()
    return news_items


@router.put("/{news_id}/status", response_model=NewsResponse)
async def update_news_status(
    news_id: UUID,
    status_in: StatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Updates the verification status of an AI-extracted corporate news signal.
    Enforces tenant isolation and validates transition status values.
    """
    workspace_id = UUID(current_user["workspace_id"])
    new_status = status_in.status.lower()

    if new_status not in ["pending", "approved", "rejected"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status. Must be 'pending', 'approved', or 'rejected'.",
        )

    await logger.ainfo(
        "update_news_status_requested",
        news_id=str(news_id),
        workspace_id=str(workspace_id),
        new_status=new_status,
    )

    # 1. Fetch and verify news item within workspace boundary
    query = select(AccountNewsModel).where(
        AccountNewsModel.id == news_id,
        AccountNewsModel.workspace_id == workspace_id,
    )
    result = await db.execute(query)
    news_item = result.scalar_one_or_none()

    if not news_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Corporate news alert not found or unauthorized.",
        )

    # 2. Update status and save
    news_item.status = new_status
    await db.commit()
    await db.refresh(news_item)

    await logger.ainfo(
        "update_news_status_completed",
        news_id=str(news_id),
        status=new_status,
    )

    return news_item
