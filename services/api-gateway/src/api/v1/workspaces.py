from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog
from uuid import UUID

from src.core.database import get_db
from src.core.auth import get_current_user, require_role
from src.domains.system.models import (
    WorkspaceModel,
    UserModel,
    UserSettingsModel,
    EmployeeConfigModel,
    WorkspaceRequestModel,
)
from src.domains.system.schemas import (
    WorkspaceCreate,
    WorkspaceResponse,
    UserCreate,
    UserResponse,
    WorkspaceRequestCreate,
    WorkspaceRequestResponse,
    InviteVerificationResponse,
    ClaimInviteRequest,
)

logger = structlog.get_logger()
router = APIRouter(tags=["Workspaces"])


@router.post("/", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    workspace_in: WorkspaceCreate, db: AsyncSession = Depends(get_db)
):
    """
    Registers a new Multi-Tenant Workspace and initializes default Digital Employee configurations.
    """
    await logger.ainfo("create_workspace_requested", name=workspace_in.name)

    # 1. Create and save the new workspace
    new_workspace = WorkspaceModel(
        name=workspace_in.name,
        company_name=workspace_in.company_name,
        industry=workspace_in.industry,
        timezone=workspace_in.timezone,
        currency=workspace_in.currency,
    )
    db.add(new_workspace)
    await db.flush()  # Generate UUID ID for FK references

    # 2. Initialize default Digital Employee configurations for this workspace
    default_employees = [
        "AccountDiscoveryEmployee",
        "CompanyResearchEmployee",
        "BuyingSignalEmployee",
    ]
    for emp_name in default_employees:
        db.add(
            EmployeeConfigModel(
                workspace_id=new_workspace.id,
                employee_name=emp_name,
                is_enabled=True,
                config={},
            )
        )

    await db.commit()
    await db.refresh(new_workspace)

    await logger.ainfo(
        "workspace_created_successfully", workspace_id=str(new_workspace.id)
    )
    return new_workspace


@router.post(
    "/request-access",
    response_model=WorkspaceRequestResponse,
    status_code=status.HTTP_201_CREATED,
)
async def request_access(
    req_in: WorkspaceRequestCreate, db: AsyncSession = Depends(get_db)
):
    """
    Submits an external request to join the platform.
    """
    await logger.ainfo(
        "request_access_received", email=req_in.email, company=req_in.company_name
    )

    # Check if request or user already exists
    req_exists = await db.execute(
        select(WorkspaceRequestModel).where(WorkspaceRequestModel.email == req_in.email)
    )
    if req_exists.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An access request with this email has already been submitted.",
        )

    user_exists = await db.execute(
        select(UserModel).where(UserModel.email == req_in.email)
    )
    if user_exists.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A registered user with this email already exists.",
        )

    new_req = WorkspaceRequestModel(
        email=req_in.email,
        full_name=req_in.full_name,
        company_name=req_in.company_name,
        industry=req_in.industry,
        reason=req_in.reason,
        status="pending",
    )
    db.add(new_req)
    await db.commit()
    await db.refresh(new_req)

    await logger.ainfo("request_access_saved", id=str(new_req.id))
    return new_req


@router.get("/verify-invite", response_model=InviteVerificationResponse)
async def verify_invite(email: str, db: AsyncSession = Depends(get_db)):
    """
    Checks if a user is invited (status='pending' in local public.users table).
    """
    await logger.ainfo("verify_invite_requested", email=email)

    result = await db.execute(
        select(UserModel).where(UserModel.email == email, UserModel.status == "pending")
    )
    user = result.scalar_one_or_none()

    if not user:
        await logger.awarn("verify_invite_failed", email=email)
        return InviteVerificationResponse(is_valid=False, email=email)

    # Fetch workspace company name
    ws_result = await db.execute(
        select(WorkspaceModel).where(WorkspaceModel.id == user.workspace_id)
    )
    workspace = ws_result.scalar_one()

    return InviteVerificationResponse(
        is_valid=True,
        email=email,
        full_name=user.full_name,
        company_name=workspace.company_name or workspace.name,
    )


@router.post("/claim-invite", response_model=UserResponse)
async def claim_invite(
    claim_in: ClaimInviteRequest, db: AsyncSession = Depends(get_db)
):
    """
    Claims an invite, changing status to active and binding it to the real Supabase Auth UUID.
    """
    await logger.ainfo(
        "claim_invite_requested",
        email=claim_in.email,
        supabase_id=str(claim_in.supabase_user_id),
    )

    # 1. Find the pending user
    result = await db.execute(
        select(UserModel).where(
            UserModel.email == claim_in.email, UserModel.status == "pending"
        )
    )
    pending_user = result.scalar_one_or_none()

    if not pending_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No pending invitation found for this email address.",
        )

    # 2. Delete the old pending record and insert a new active record with the correct UUID.
    workspace_id = pending_user.workspace_id
    role = pending_user.role

    await db.delete(pending_user)
    await db.flush()

    # 3. Create the new active user
    active_user = UserModel(
        id=claim_in.supabase_user_id,
        workspace_id=workspace_id,
        email=claim_in.email,
        full_name=claim_in.full_name,
        role=role,
        status="active",
    )
    db.add(active_user)
    await db.flush()

    # 4. Create empty settings profile
    db.add(
        UserSettingsModel(
            user_id=active_user.id,
            workspace_id=workspace_id,
            notification_preferences={},
            display_preferences={},
        )
    )

    await db.commit()
    await db.refresh(active_user)

    await logger.ainfo("invite_claimed_successfully", user_id=str(active_user.id))
    return active_user


@router.get("/users/me", response_model=UserResponse)
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """
    Returns the currently authenticated user's profile metadata.
    """
    return current_user


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(
    workspace_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Fetches the details of a specific workspace.
    """
    if workspace_id != UUID(current_user["workspace_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this workspace details",
        )
    result = await db.execute(
        select(WorkspaceModel).where(
            WorkspaceModel.id == workspace_id, WorkspaceModel.deleted_at.is_(None)
        )
    )
    workspace = result.scalar_one_or_none()

    if not workspace:
        await logger.awarn("workspace_not_found", workspace_id=str(workspace_id))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace with ID {workspace_id} not found",
        )

    return workspace


@router.post(
    "/{workspace_id}/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_workspace_user(
    workspace_id: UUID,
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role(["administrator"])),
):
    """
    Adds a new user to a workspace and creates default personal settings.
    """
    if workspace_id != UUID(current_user["workspace_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot add users to another workspace",
        )
    await logger.ainfo(
        "add_workspace_user_requested",
        email=user_in.email,
        workspace_id=str(workspace_id),
    )

    # 1. Check if workspace exists
    ws_result = await db.execute(
        select(WorkspaceModel).where(WorkspaceModel.id == workspace_id)
    )
    workspace = ws_result.scalar_one_or_none()
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace with ID {workspace_id} not found",
        )

    # 2. Check if email already exists
    user_result = await db.execute(
        select(UserModel).where(UserModel.email == user_in.email)
    )
    existing_user = user_result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists",
        )

    # 3. Create the new user in database
    new_user = UserModel(
        workspace_id=workspace_id,
        email=user_in.email,
        full_name=user_in.full_name,
        role=user_in.role,
        status="pending",
    )
    db.add(new_user)
    await db.flush()  # Generate new_user.id for FK

    # 4. Create empty settings profile for user
    db.add(
        UserSettingsModel(
            user_id=new_user.id,
            workspace_id=workspace_id,
            notification_preferences={},
            display_preferences={},
        )
    )

    await db.commit()
    await db.refresh(new_user)

    await logger.ainfo(
        "user_added_successfully",
        user_id=str(new_user.id),
        workspace_id=str(workspace_id),
    )
    return new_user
