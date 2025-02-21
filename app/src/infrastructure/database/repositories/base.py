from typing import TypeVar, Generic, Type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from infrastructure.database.base import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get_by_id(self, session: AsyncSession, id: int) -> ModelType | None:
        query = select(self.model).filter(self.model.id == id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(self, session: AsyncSession) -> list[ModelType]:
        query = select(self.model)
        result = await session.execute(query)
        return result.scalars().all()

    async def create(self, session: AsyncSession, **kwargs) -> ModelType:
        instance = self.model(**kwargs)
        session.add(instance)
        await session.commit()
        await session.refresh(instance)
        return instance

    async def update(self, session: AsyncSession, id: int, **kwargs) -> ModelType | None:
        instance = await self.get_by_id(session, id)
        if instance:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            await session.commit()
            await session.refresh(instance)
        return instance

    async def delete(self, session: AsyncSession, id: int) -> bool:
        instance = await self.get_by_id(session, id)
        if instance:
            await session.delete(instance)
            await session.commit()
            return True
        return False