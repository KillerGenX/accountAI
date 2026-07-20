import asyncio
import os
import sys
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context
from dotenv import load_dotenv

# Add project root and FastAPI services directory to Python import path
# This allows Alembic to import the models and database configuration successfully
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(os.path.dirname(__file__), "../services/api-gateway"))

# Load environment variables from the root folder .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.env"))

# Import target declarative models metadata
from src.core.database import Base
# Import system models
from src.domains.system.models import WorkspaceModel, UserModel, UserSettingsModel, EmployeeConfigModel, WorkspaceRequestModel
# Import account models
from src.domains.account.models import (
    AccountModel,
    ContactModel,
    AccountIntelligenceModel,
    AccountNewsModel,
    AccountNoteModel,
    AccountEmbeddingModel,
    AccountDocumentModel,
    AccountDocumentChunkModel,
)

# This is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the target metadata for autogenerate support
target_metadata = Base.metadata

# Retrieve database connection string from environment variables
database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise ValueError("DATABASE_URL is not set in environment variables")

# Ensure the database URL uses the asyncpg driver for async SQLAlchemy
if database_url.startswith("postgresql://"):
    async_db_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
elif database_url.startswith("postgres://"):
    async_db_url = database_url.replace("postgres://", "postgresql+asyncpg://", 1)
else:
    async_db_url = database_url

# Override the main sqlalchemy.url option in alembic.ini with the environment variable
# Escape '%' as '%%' to prevent configparser interpolation errors (e.g. for URL-encoded passwords)
config.set_main_option("sqlalchemy.url", async_db_url.replace("%", "%%"))


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Helper method to run migrations synchronously within the async connection."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode using async connection."""
    url = config.get_main_option("sqlalchemy.url")
    
    # Configure connect_args to disable prepared statements on pg_bouncer (port 6543)
    connect_args = {}
    if "6543" in url:
        connect_args["statement_cache_size"] = 0

    connectable = create_async_engine(
        url,
        poolclass=pool.NullPool,
        connect_args=connect_args
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    # Run the async loop for online migrations
    asyncio.run(run_migrations_online())
