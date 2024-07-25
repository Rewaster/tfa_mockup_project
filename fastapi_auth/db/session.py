from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from fastapi_auth.core.config import settings

# XXX session and engine
engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    future=True,
    echo=True,
)
SessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
