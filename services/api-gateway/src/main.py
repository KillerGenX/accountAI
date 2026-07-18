import os
import sys
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import structlog
from dotenv import load_dotenv
from sqlalchemy import text

# Load env variables from root/parent folder
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../../.env"))

# Configure sys.path so 'src' packages can be imported successfully
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ]
)
logger = structlog.get_logger()

# Import database session maker, NATS client, and routers
from src.core.database import async_session_maker  # noqa: E402
from src.core.nats_client import nats_client  # noqa: E402
from src.api.v1.workspaces import router as workspaces_router  # noqa: E402
from src.api.v1.accounts import router as accounts_router  # noqa: E402
from src.api.v1.search import router as search_router  # noqa: E402
from src.api.v1.monitoring import router as monitoring_router  # noqa: E402
from src.api.v1.news import router as news_router  # noqa: E402
from src.api.v1.documents import router as documents_router  # noqa: E402

app = FastAPI(
    title="PROJECT BRAIN API Gateway",
    description="Enterprise API Gateway for Account Intelligence Platform",
    version="1.0.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register NATS connection lifecycle handlers
@app.on_event("startup")
async def startup_event():
    await nats_client.connect()


@app.on_event("shutdown")
async def shutdown_event():
    await nats_client.close()


# Register Domain Routers
app.include_router(workspaces_router, prefix="/api/v1/workspaces")
app.include_router(accounts_router, prefix="/api/v1/accounts")
app.include_router(search_router, prefix="/api/v1/search")
app.include_router(monitoring_router, prefix="/api/v1/monitoring")
app.include_router(news_router, prefix="/api/v1/news")
app.include_router(documents_router, prefix="/api/v1/documents")



class HealthStatus(BaseModel):
    status: str
    environment: str
    supabase_connected: bool


@app.get("/health", response_model=HealthStatus, status_code=status.HTTP_200_OK)
async def health_check():
    """
    Checks the status of the API Gateway and executes a query to verify Supabase DB connection.
    """
    supabase_connected = False
    try:
        # Run a simple SELECT 1 query to verify database is online and reachable
        async with async_session_maker() as session:
            await session.execute(text("SELECT 1"))
            supabase_connected = True
    except Exception as e:
        await logger.aerror("health_check_db_connection_failed", error=str(e))

    await logger.ainfo(
        "health_check_triggered", environment=os.getenv("ENVIRONMENT", "development")
    )
    return {
        "status": "healthy",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "supabase_connected": supabase_connected,
    }


@app.get("/api/v1")
async def root():
    return {"message": "Welcome to PROJECT BRAIN API Gateway v1", "docs_url": "/docs"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
