from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog
from uuid import UUID

from src.core.database import get_db
from src.domains.system.models import WorkspaceModel, UserModel, UserSettingsModel, EmployeeConfigModel
from src.domains.system.schemas import WorkspaceCreate, WorkspaceResponse, UserCreate, UserResponse

logger = structlog.get_logger()
router = APIRouter(tags=["Workspaces"])

@router.post("/", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
async def create_workspace(workspace_in: WorkspaceCreate, db: AsyncSession = Depends(get_db)):
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
        currency=workspace_in.currency
    )
    db.add(new_workspace)
    await db.flush()  # Generate UUID ID for FK references
    
    # 2. Initialize default Digital Employee configurations for this workspace
    default_employees = [
        "AccountDiscoveryEmployee",
        "CompanyResearchEmployee",
        "BuyingSignalEmployee"
    ]
    for emp_name in default_employees:
        db.add(EmployeeConfigModel(
            workspace_id=new_workspace.id,
            employee_name=emp_name,
            is_enabled=True,
            config={}
        ))
        
    await db.commit()
    await db.refresh(new_workspace)
    
    await logger.ainfo("workspace_created_successfully", workspace_id=str(new_workspace.id))
    return new_workspace

@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(workspace_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Fetches the details of a specific workspace.
    """
    result = await db.execute(
        select(WorkspaceModel).where(WorkspaceModel.id == workspace_id, WorkspaceModel.deleted_at.is_(None))
    )
    workspace = result.scalar_one_or_none()
    
    if not workspace:
        await logger.awarn("workspace_not_found", workspace_id=str(workspace_id))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace with ID {workspace_id} not found"
        )
        
    return workspace

@router.post("/{workspace_id}/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def add_workspace_user(
    workspace_id: UUID, 
    user_in: UserCreate, 
    db: AsyncSession = Depends(get_db)
):
    """
    Adds a new user to a workspace and creates default personal settings.
    """
    await logger.ainfo("add_workspace_user_requested", email=user_in.email, workspace_id=str(workspace_id))

    # 1. Check if workspace exists
    ws_result = await db.execute(select(WorkspaceModel).where(WorkspaceModel.id == workspace_id))
    workspace = ws_result.scalar_one_or_none()
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace with ID {workspace_id} not found"
        )

    # 2. Check if email already exists
    user_result = await db.execute(select(UserModel).where(UserModel.email == user_in.email))
    existing_user = user_result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists"
        )

    # 3. Create the new user in database
    new_user = UserModel(
        workspace_id=workspace_id,
        email=user_in.email,
        full_name=user_in.full_name,
        role=user_in.role,
        status="pending"
    )
    db.add(new_user)
    await db.flush() # Generate new_user.id for FK

    # 4. Create empty settings profile for user
    db.add(UserSettingsModel(
        user_id=new_user.id,
        workspace_id=workspace_id,
        notification_preferences={},
        display_preferences={}
    ))

    await db.commit()
    await db.refresh(new_user)
    
    await logger.ainfo("user_added_successfully", user_id=str(new_user.id), workspace_id=str(workspace_id))
    return new_user
