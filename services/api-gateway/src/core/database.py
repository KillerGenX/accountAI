import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv

# Load env variables from root/parent folder
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../../.env"))

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in environment variables")

# SQLAlchemy connection string must use asyncpg driver for async connections
# Supabase connection pooler uses postgresql://, we convert to postgresql+asyncpg://
if DATABASE_URL.startswith("postgresql://"):
    ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgres://"):
    ASYNC_DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
else:
    ASYNC_DATABASE_URL = DATABASE_URL

# Configure connect_args to disable prepared statements on pg_bouncer (port 6543)
connect_args = {}
if "6543" in ASYNC_DATABASE_URL:
    connect_args["statement_cache_size"] = 0

# Create the asynchronous SQLAlchemy database engine
# pool_pre_ping=True forces the connection pool to test connections before using them
# (crucial for Supabase connection pooler timeouts)
engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,  # Set to True for SQL queries logging during development
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    connect_args=connect_args
)

# Create session maker factory for generating async database sessions
async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Declarative Base for models definition
Base = declarative_base()

# FastAPI Dependency injection provider for DB sessions
async def get_db():
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
