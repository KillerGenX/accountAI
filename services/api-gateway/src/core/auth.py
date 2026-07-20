import os
import json
import hashlib
import httpx
import structlog
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import redis.asyncio as aioredis

from src.core.database import get_db
from src.domains.system.models import UserModel

logger = structlog.get_logger()
oauth2_scheme = HTTPBearer(auto_error=False)

# Redis client initialization
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = aioredis.from_url(redis_url, encoding="utf-8", decode_responses=True)


async def get_cached_user(token_hash: str) -> dict | None:
    """
    Attempts to retrieve user session details from Redis cache.
    """
    try:
        data = await redis_client.get(f"auth_session:{token_hash}")
        if data:
            return json.loads(data)
    except Exception as e:
        logger.error("redis_cache_get_failed", error=str(e))
    return None


async def set_cached_user(token_hash: str, user_data: dict) -> None:
    """
    Caches user session details in Redis for 300 seconds (5 minutes).
    """
    try:
        await redis_client.setex(
            f"auth_session:{token_hash}", 300, json.dumps(user_data)
        )
    except Exception as e:
        logger.error("redis_cache_set_failed", error=str(e))


async def verify_supabase_token(token: str) -> dict:
    """
    Verifies JWT token validity by calling Supabase Auth API directly.
    Supports a mock token bypass in local development mode.
    """
    # Local development mock bypass
    if os.getenv("ENVIRONMENT") == "development" and token == "mock-token-teguh":
        return {
            "id": "5651b60c-a77f-4037-a190-f9e9a7c6eb02",  # Match system's mock user ID
            "email": "am_teguh@company.com",
        }

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_anon_key = os.getenv("SUPABASE_ANON_KEY")

    if not supabase_url or not supabase_anon_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supabase Auth configurations are missing on server",
        )

    url = f"{supabase_url}/auth/v1/user"
    headers = {"Authorization": f"Bearer {token}", "apikey": supabase_anon_key}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=10.0)
            if response.status_code != 200:
                logger.warning(
                    "supabase_token_verification_failed",
                    status_code=response.status_code,
                    body=response.text,
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired authentication token",
                )
            return response.json()
        except httpx.RequestError as req_err:
            logger.error("supabase_auth_request_failed", error=str(req_err))
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication server temporarily unreachable",
            )


async def get_current_user(
    auth: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    FastAPI dependency that extracts and validates the Bearer token.
    Enforces multi-tenant isolation by checking the user's workspace in the local DB.
    """
    if not auth:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization Header",
        )

    token = auth.credentials
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()

    # 1. Try Redis cache first
    cached_user = await get_cached_user(token_hash)
    if cached_user:
        return cached_user

    # 2. Call Supabase Auth API
    supabase_user = await verify_supabase_token(token)

    user_id = supabase_user["id"]
    email = supabase_user.get("email")

    # 3. Check if user exists in local database and get their workspace/role info
    stmt = select(UserModel).where(
        UserModel.id == user_id, UserModel.deleted_at.is_(None)
    )
    result = await db.execute(stmt)
    db_user = result.scalar_one_or_none()

    if not db_user:
        logger.warning(
            "user_authenticated_by_supabase_but_not_in_db", email=email, user_id=user_id
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is authenticated but not registered in the system",
        )

    # 4. Construct current user profile dict
    current_user = {
        "id": str(db_user.id),
        "workspace_id": str(db_user.workspace_id),
        "email": db_user.email,
        "role": db_user.role,
        "full_name": db_user.full_name,
        "status": db_user.status,
        "invited_by": str(db_user.invited_by) if db_user.invited_by else None,
        "invited_at": db_user.invited_at.isoformat() if db_user.invited_at else None,
        "joined_at": db_user.joined_at.isoformat() if db_user.joined_at else None,
        "last_login_at": (
            db_user.last_login_at.isoformat() if db_user.last_login_at else None
        ),
        "created_at": db_user.created_at.isoformat() if db_user.created_at else None,
        "updated_at": db_user.updated_at.isoformat() if db_user.updated_at else None,
    }

    # 5. Cache the verified profile
    await set_cached_user(token_hash, current_user)

    return current_user


class RoleChecker:
    """
    FastAPI dependency for Role-Based Access Control (RBAC).
    """

    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: dict = Depends(get_current_user)) -> dict:
        if user["role"] not in self.allowed_roles:
            logger.warning(
                "role_access_denied",
                user_role=user["role"],
                allowed_roles=self.allowed_roles,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource",
            )
        return user


def require_role(roles: list[str]):
    return RoleChecker(roles)
