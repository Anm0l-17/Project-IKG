from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

# Engine options
connect_args = {}
if settings.DATABASE_SSL in ("require", "verify-full"):
    connect_args["ssl"] = settings.DATABASE_SSL

# Create Async Engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.APP_ENV == "development",
    future=True,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    connect_args=connect_args,
)

# Async Session Factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Base declarative class for all SQLAlchemy ORM models."""
    pass


async def get_db():
    """Dependency provider for AsyncSession."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
