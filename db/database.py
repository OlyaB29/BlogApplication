from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import settings

Base = declarative_base()

# ASYNC_DATABASE_URL = 'postgresql+asyncpg://{}:{}@{}:5432/{}'.format(settings.DB_USER, settings.DB_PASS,
#                                                                     settings.DB_HOST, settings.DB_NAME)

ASYNC_DATABASE_URL = settings.ASYNC_DATABASE_URL
async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=True, future=True)
AsyncSessionLocal = sessionmaker(
    expire_on_commit=False,
    class_=AsyncSession,
    bind=async_engine,
)

SYNC_DATABASE_URL = 'postgresql://{}:{}@{}:5432/{}'.format(settings.DB_USER, settings.DB_PASS,
                                                                    settings.DB_HOST, settings.DB_NAME)
sync_engine = create_engine(SYNC_DATABASE_URL, echo=True)
SyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine,
)
