from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import structlog
from uuid import UUID
from typing import List

from src.core.database import get_db
from src.core.auth import get_current_user
from src.domains.account.models import AccountModel, AccountEmbeddingModel
from src.domains.account.embeddings import embedding_client
from src.domains.account.schemas import AccountResponse
from pydantic import BaseModel

logger = structlog.get_logger()
router = APIRouter(tags=["Search"])


class AccountSearchResponse(BaseModel):
    account: AccountResponse
    similarity_score: float


@router.get("/accounts", response_model=List[AccountSearchResponse])
async def search_accounts(
    q: str = Query(..., min_length=1, description="Semantic search query"),
    limit: int = Query(10, ge=1, le=50, description="Max search results to return"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Performs a semantic search on corporate accounts under a workspace using pgvector.
    Queries the vector database against account summaries, contacts, and personal notes.
    """
    workspace_id = UUID(current_user["workspace_id"])
    await logger.ainfo(
        "semantic_search_requested", query=q, workspace_id=str(workspace_id)
    )

    # 1. Generate embedding vector for the search query
    try:
        query_vector = await embedding_client.get_embedding(q)
    except Exception as e:
        await logger.aerror("search_embedding_generation_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process search query embedding",
        )

    # 2. Query database for nearest neighbors using pgvector cosine distance
    try:
        # Distance calculation in pgvector via SQLAlchemy: column.cosine_distance(vector)
        distance_col = AccountEmbeddingModel.embedding.cosine_distance(
            query_vector
        ).label("distance")

        stmt = (
            select(AccountModel, func.min(distance_col).label("min_distance"))
            .join(
                AccountEmbeddingModel,
                AccountEmbeddingModel.account_id == AccountModel.id,
            )
            .where(
                AccountModel.workspace_id == workspace_id,
                AccountModel.deleted_at.is_(None),
            )
            .group_by(AccountModel.id)
            .order_by("min_distance")
            .limit(limit)
        )

        result = await db.execute(stmt)
        rows = result.all()

        search_results = []
        for account, min_distance in rows:
            # Cosine similarity = 1 - Cosine distance
            similarity = 1.0 - float(min_distance) if min_distance is not None else 0.0

            # Map similarity to a 0.0 - 1.0 range safely
            similarity = max(0.0, min(1.0, similarity))

            search_results.append(
                AccountSearchResponse(
                    account=AccountResponse.model_validate(account),
                    similarity_score=round(similarity, 4),
                )
            )

        await logger.ainfo(
            "semantic_search_completed", results_count=len(search_results)
        )
        return search_results

    except Exception as e:
        await logger.aerror("semantic_search_database_query_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database query failed during semantic search: {str(e)}",
        )
