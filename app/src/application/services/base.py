import logging
import sentry_sdk
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from infrastructure.database.session import db

logger = logging.getLogger(__name__)

class BaseService:
    def __init__(self, model):
        self.model = model

    async def _execute_with_session(self, operation):
        async with db.session() as session:
            async with session.begin():
                try:
                    return await operation(session)
                except IntegrityError as e:
                    sentry_sdk.capture_exception(e)
                    logger.error(f"Integrity error in {self.model.__name__}: {e.orig}")
                    await session.rollback()
                    raise
                except SQLAlchemyError as e:
                    sentry_sdk.capture_exception(e)
                    logger.error(f"SQLAlchemy error in {self.model.__name__}: {e}")
                    await session.rollback()
                    raise
                except Exception as e:
                    sentry_sdk.capture_exception(e)
                    logger.error(f"Unexpected error in {self.model.__name__}: {e}")
                    await session.rollback()
                    raise

    async def get_all(self):
        async def operation(session):
            query = select(self.model)
            result = await session.execute(query)
            return result.scalars().all()
        return await self._execute_with_session(operation)

    async def get_by_field(self, field, value):
        async def operation(session):
            query = select(self.model).where(getattr(self.model, field) == value)
            result = await session.execute(query)
            return result.scalars().first()
        return await self._execute_with_session(operation)

    async def create(self, **kwargs):
        async def operation(session):
            instance = self.model(**kwargs)
            session.add(instance)
            await session.commit()
            return instance
        return await self._execute_with_session(operation)

    async def update(self, field_name, field_value, **kwargs):
        async def operation(session):
            instance = await self.get_by_field(field_name, field_value)
            if not instance:
                logger.warning(
                    f"{self.model.__name__} with {field_name}={field_value} not found"
                )
                return None

            for key, value in kwargs.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)

            session.add(instance)
            await session.commit()
            return instance
        return await self._execute_with_session(operation)

    async def upsert(self, field_name, field_value, **kwargs):
        async def operation(session):
            query = select(self.model).where(getattr(self.model, field_name) == field_value)
            result = await session.execute(query)
            instance = result.scalars().first()

            if instance:
                for key, value in kwargs.items():
                    if hasattr(instance, key):
                        setattr(instance, key, value)
                session.add(instance)
            else:
                instance = self.model(**kwargs)
                setattr(instance, field_name, field_value)
                session.add(instance)

            await session.commit()
            return instance

        return await self._execute_with_session(operation)