from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog
from uuid import UUID
from typing import List, Optional

from src.core.database import get_db
from src.core.nats_client import nats_client
from src.domains.account.models import (
    AccountModel,
    ContactModel,
    AccountNoteModel,
    AccountEmbeddingModel,
)
from src.domains.account.embeddings import embedding_client
from src.domains.system.models import WorkspaceModel, UserModel
from src.core.auth import get_current_user, require_role
from src.domains.account.schemas import (
    AccountCreate,
    AccountResponse,
    ContactCreate,
    ContactResponse,
    NoteCreate,
    NoteResponse,
)

logger = structlog.get_logger()
router = APIRouter(tags=["Accounts"])


@router.post("/", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    account_in: AccountCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role(["administrator", "account_manager"])),
):
    """
    Registers a new corporate account manually under a specific workspace.
    """
    await logger.ainfo(
        "create_account_requested",
        name=account_in.company_name,
        workspace_id=str(account_in.workspace_id),
    )

    # Verify tenant isolation
    if str(account_in.workspace_id) != current_user["workspace_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot register an account outside your workspace",
        )

    # 1. Verify workspace exists
    ws_result = await db.execute(
        select(WorkspaceModel).where(WorkspaceModel.id == account_in.workspace_id)
    )
    workspace = ws_result.scalar_one_or_none()
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace with ID {account_in.workspace_id} not found",
        )

    # 2. Verify assigned user exists (if provided)
    if account_in.assigned_to:
        user_result = await db.execute(
            select(UserModel).where(UserModel.id == account_in.assigned_to)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Assigned User with ID {account_in.assigned_to} not found",
            )

    # 3. Create the account record
    new_account = AccountModel(
        workspace_id=account_in.workspace_id,
        company_name=account_in.company_name,
        company_url=account_in.company_url,
        industry=account_in.industry,
        sub_industry=account_in.sub_industry,
        company_size=account_in.company_size,
        employee_count_min=account_in.employee_count_min,
        employee_count_max=account_in.employee_count_max,
        headquarters=account_in.headquarters,
        founded_year=account_in.founded_year,
        assigned_to=account_in.assigned_to,
        status="active",
        source="manual",
        completeness_score=15,  # Default base score for manual initialization
    )
    db.add(new_account)
    await db.commit()
    await db.refresh(new_account)

    # Publish account.created event to NATS event bus
    try:
        event_payload = {
            "id": str(new_account.id),
            "company_name": new_account.company_name,
            "workspace_id": str(new_account.workspace_id),
        }
        await nats_client.publish("account.created", event_payload)
    except Exception as e:
        await logger.aerror(
            "nats_publish_account_created_failed",
            account_id=str(new_account.id),
            error=str(e),
        )

    await logger.ainfo("account_created_successfully", account_id=str(new_account.id))

    # 4. Generate and save embedding for the new account summary
    try:
        text_to_embed = f"Company Name: {new_account.company_name}. Industry: {new_account.industry or 'Unknown'}. Sub-industry: {new_account.sub_industry or 'Unknown'}."
        vector = await embedding_client.get_embedding(text_to_embed)
        new_embedding = AccountEmbeddingModel(
            account_id=new_account.id,
            content_type="summary",
            embedding=vector,
            source_record_id=new_account.id,
        )
        db.add(new_embedding)
        await db.commit()
    except Exception as emb_err:
        await logger.aerror(
            "account_embedding_creation_failed",
            account_id=str(new_account.id),
            error=str(emb_err),
        )

    return new_account


@router.get("/", response_model=List[AccountResponse])
async def list_accounts(
    assigned_to: Optional[UUID] = Query(
        None, description="Filter accounts by assigned AM UUID"
    ),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Lists accounts under a workspace, optionally filtered by assigned Account Manager.
    """
    workspace_id = UUID(current_user["workspace_id"])
    stmt = select(AccountModel).where(
        AccountModel.workspace_id == workspace_id, AccountModel.deleted_at.is_(None)
    )
    if assigned_to:
        stmt = stmt.where(AccountModel.assigned_to == assigned_to)

    result = await db.execute(stmt)
    accounts = result.scalars().all()
    return accounts


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Fetches details of a specific corporate account by ID.
    """
    result = await db.execute(
        select(AccountModel).where(
            AccountModel.id == account_id,
            AccountModel.workspace_id == UUID(current_user["workspace_id"]),
            AccountModel.deleted_at.is_(None),
        )
    )
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account with ID {account_id} not found in your workspace",
        )
    return account


@router.get("/{account_id}/contacts", response_model=List[ContactResponse])
async def list_account_contacts(
    account_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Lists contacts mapped to a specific corporate account.
    """
    # Verify account exists and belongs to the workspace
    acc_res = await db.execute(
        select(AccountModel).where(
            AccountModel.id == account_id,
            AccountModel.workspace_id == UUID(current_user["workspace_id"]),
            AccountModel.deleted_at.is_(None),
        )
    )
    if not acc_res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found in your workspace",
        )

    result = await db.execute(
        select(ContactModel).where(
            ContactModel.account_id == account_id, ContactModel.deleted_at.is_(None)
        )
    )
    return result.scalars().all()


@router.post(
    "/{account_id}/contacts",
    response_model=ContactResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_account_contact(
    account_id: UUID,
    contact_in: ContactCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role(["administrator", "account_manager"])),
):
    """
    Adds a new contact to a corporate account manually.
    """
    # 1. Fetch account to extract workspace_id and check existence
    acc_res = await db.execute(
        select(AccountModel).where(
            AccountModel.id == account_id,
            AccountModel.workspace_id == UUID(current_user["workspace_id"]),
            AccountModel.deleted_at.is_(None),
        )
    )
    account = acc_res.scalar_one_or_none()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found in your workspace",
        )

    # 2. Add contact record
    new_contact = ContactModel(
        workspace_id=account.workspace_id,
        account_id=account_id,
        full_name=contact_in.full_name,
        title=contact_in.title,
        department=contact_in.department,
        seniority=contact_in.seniority,
        buying_role=contact_in.buying_role,
        linkedin_url=contact_in.linkedin_url,
        email=contact_in.email,
        phone=contact_in.phone,
        is_primary=contact_in.is_primary,
    )
    db.add(new_contact)

    # 3. Recalculate completeness score slightly for adding a contact
    account.completeness_score = min(100, account.completeness_score + 5)

    await db.commit()
    await db.refresh(new_contact)

    # 4. Generate embedding for the contact
    try:
        text_to_embed = f"Contact: {new_contact.full_name}. Title: {new_contact.title or 'Unknown'}. Department: {new_contact.department or 'Unknown'}. Seniority: {new_contact.seniority or 'Unknown'}. Buying Role: {new_contact.buying_role or 'Unknown'}."
        vector = await embedding_client.get_embedding(text_to_embed)
        new_embedding = AccountEmbeddingModel(
            account_id=account_id,
            content_type="contact",
            embedding=vector,
            source_record_id=new_contact.id,
        )
        db.add(new_embedding)
        await db.commit()
    except Exception as emb_err:
        await logger.aerror(
            "contact_embedding_creation_failed",
            contact_id=str(new_contact.id),
            error=str(emb_err),
        )

    return new_contact


@router.get("/{account_id}/notes", response_model=List[NoteResponse])
async def list_account_notes(
    account_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Retrieves private notes for an account. Stored notes are private to the AM who authored them.
    """
    result = await db.execute(
        select(AccountNoteModel).where(
            AccountNoteModel.account_id == account_id,
            AccountNoteModel.user_id == UUID(current_user["id"]),
            AccountNoteModel.deleted_at.is_(None),
        )
    )
    return result.scalars().all()


@router.post(
    "/{account_id}/notes",
    response_model=NoteResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_account_note(
    account_id: UUID,
    note_in: NoteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Adds a private personal note for an account (accessible only by the author).
    """
    # 1. Fetch account to check existence and extract workspace_id
    acc_res = await db.execute(
        select(AccountModel).where(
            AccountModel.id == account_id,
            AccountModel.workspace_id == UUID(current_user["workspace_id"]),
            AccountModel.deleted_at.is_(None),
        )
    )
    account = acc_res.scalar_one_or_none()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found in your workspace",
        )

    # 2. Verify note author matches the authenticated user
    if str(note_in.user_id) != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot write a note on behalf of another user",
        )

    user_res = await db.execute(
        select(UserModel).where(
            UserModel.id == note_in.user_id,
            UserModel.workspace_id == account.workspace_id,
        )
    )
    if not user_res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Author User not found in this workspace",
        )

    # 3. Create note record
    new_note = AccountNoteModel(
        workspace_id=account.workspace_id,
        account_id=account_id,
        user_id=note_in.user_id,
        content=note_in.content,
    )
    db.add(new_note)
    await db.commit()
    await db.refresh(new_note)

    # 4. Generate embedding for the note
    try:
        text_to_embed = f"Personal Note: {new_note.content}"
        vector = await embedding_client.get_embedding(text_to_embed)
        new_embedding = AccountEmbeddingModel(
            account_id=account_id,
            content_type="note",
            embedding=vector,
            source_record_id=new_note.id,
        )
        db.add(new_embedding)
        await db.commit()
    except Exception as emb_err:
        await logger.aerror(
            "note_embedding_creation_failed",
            note_id=str(new_note.id),
            error=str(emb_err),
        )

    return new_note
