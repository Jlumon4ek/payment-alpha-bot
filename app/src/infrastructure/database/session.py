from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from core.config import settings

class DatabaseSessionManager:
    def __init__(self):
        self._engine = None
        self._session_factory = None

    def init(self):
        database_url = (
            f"postgresql+asyncpg://{settings.POSTGRES_USER}:"
            f"{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:"
            f"{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
        )
        
        self._engine = create_async_engine(
            database_url,
            pool_pre_ping=True    
        )
        
        self._session_factory = sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False
        )

    @asynccontextmanager
    async def session(self):
        if self._session_factory is None:
            self.init()

        session: AsyncSession = self._session_factory()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

db = DatabaseSessionManager()