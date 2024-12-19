from database import get_session
from sqlalchemy.sql.expression import select
from sqlalchemy import literal_column, select, union_all, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import select, update
from loguru import logger
from bot.admin.models import Admins

class AdminService:
    async def get_by_telegram_id(self, telegram_id: int):
        async with get_session() as session:
            async with session.begin():
                query = select(Admins).where(Admins.telegram_id == telegram_id)
                result = await session.execute(query)
                user = result.scalars().first()
                return user
    
    async def create(self, telegram_id: int, username: str = None, full_name: str = None):
        async with get_session() as session:
            async with session.begin():
                user = Admins(telegram_id=telegram_id, username=username, full_name=full_name)
                session.add(user)
                try:
                    await session.commit()
                except IntegrityError:
                    await session.rollback()
                    return None
                return user
            
    async def update(self, telegram_id: int, **kwargs):
        async with get_session() as session:
            try:
                result = await session.execute(
                    select(Admins).where(Admins.telegram_id == telegram_id)
                )
                user = result.scalars().first()

                if not user:
                    logger.warning(f"Admins with telegram_id {telegram_id} not found in update_user.")
                    return

                for key, value in kwargs.items():
                    if hasattr(user, key):
                        setattr(user, key, value)

                try:
                    session.add(user)
                    await session.commit()
                    logger.info(f"Admins with telegram_id {telegram_id} successfully updated with wallets.")
                except IntegrityError as e:
                    logger.error(f"Integrity error during commit: {e.orig}")
                    await session.rollback()
                    raise
                except SQLAlchemyError as e:
                    logger.error(f"SQLAlchemy error during commit: {e}")
                    await session.rollback()
                    raise
                except Exception as e:
                    logger.error(f"Unexpected error during commit: {e}")
                    await session.rollback()
                    raise

            except Exception as e:
                logger.error(f"Failed to execute update_user for telegram_id {telegram_id}: {e}")
                raise


admin_service = AdminService()