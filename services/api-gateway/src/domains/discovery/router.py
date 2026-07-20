from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
import uuid
import json

from src.core.database import get_db
from src.core.nats_client import nats_client
from src.domains.discovery.models import Prospect
from src.domains.account.models import AccountModel

router = APIRouter(prefix="/discovery", tags=["Discovery"])


class DiscoveryRequest(BaseModel):
    workspace_id: str
    criteria: str


class ApproveRequest(BaseModel):
    workspace_id: str


@router.post("/trigger")
async def trigger_discovery(req: DiscoveryRequest):
    """
    Triggers the AI worker to discover new accounts based on the provided criteria.
    """
    event_data = {"workspace_id": req.workspace_id, "criteria": req.criteria}

    await nats_client.publish("prospecting.requested", event_data)

    return {"status": "success", "message": "Discovery worker triggered."}


@router.get("/prospects")
async def get_prospects(workspace_id: str, db: AsyncSession = Depends(get_db)):
    """
    Gets all pending prospects for the workspace.
    """
    stmt = (
        select(Prospect)
        .where(
            Prospect.workspace_id == workspace_id,
            Prospect.status == "pending",
            Prospect.deleted_at == None,
        )
        .order_by(Prospect.created_at.desc())
    )

    result = await db.execute(stmt)
    prospects = result.scalars().all()

    return prospects


@router.post("/prospects/{prospect_id}/approve")
async def approve_prospect(
    prospect_id: str, req: ApproveRequest, db: AsyncSession = Depends(get_db)
):
    """
    Approves a prospect and converts it to an Account.
    """
    stmt = select(Prospect).where(
        Prospect.id == prospect_id,
        Prospect.workspace_id == req.workspace_id,
        Prospect.deleted_at == None,
    )
    result = await db.execute(stmt)
    prospect = result.scalar_one_or_none()

    if not prospect:
        raise HTTPException(status_code=404, detail="Prospect not found")

    prospect.status = "approved"

    # Create the account
    new_account = AccountModel(
        workspace_id=req.workspace_id,
        company_name=prospect.company_name,
        industry="Unknown",
        website=prospect.source_url,
    )
    db.add(new_account)
    await db.commit()

    return {"status": "success", "account_id": new_account.id}


@router.post("/prospects/{prospect_id}/reject")
async def reject_prospect(
    prospect_id: str, req: ApproveRequest, db: AsyncSession = Depends(get_db)
):
    """
    Rejects a prospect.
    """
    stmt = select(Prospect).where(
        Prospect.id == prospect_id,
        Prospect.workspace_id == req.workspace_id,
        Prospect.deleted_at == None,
    )
    result = await db.execute(stmt)
    prospect = result.scalar_one_or_none()

    if not prospect:
        raise HTTPException(status_code=404, detail="Prospect not found")

    prospect.status = "rejected"
    await db.commit()

    return {"status": "success"}
