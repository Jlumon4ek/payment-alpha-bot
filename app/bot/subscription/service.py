import datetime
from database import get_session
from sqlalchemy.sql.expression import select
from sqlalchemy import literal_column, select, union_all, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import select, update
from loguru import logger
from bot.subscription.models import Payments, Subscription

class SubscriptionService:
    async def add_payment(
            self, 
            telegram_id: int, 
            store_name: str, 
            receipt_id: str, 
            full_name: str, 
            passport_id: str,
            price: float,
            payment_date: datetime.datetime
        ):
        async with get_session() as session:
            async with session.begin():
                payment = Payments(telegram_id=telegram_id, store_name=store_name, receipt_id=receipt_id, full_name=full_name, passport_id=passport_id, price=price, payment_date=payment_date)
                session.add(payment)
                try:
                    await session.commit()
                except IntegrityError:
                    await session.rollback()
                    return None
                return payment
        
    async def get_payment(self, receipt_id: str):
        async with get_session() as session:
            async with session.begin():
                query = select(Payments).where(Payments.receipt_id == receipt_id)
                result = await session.execute(query)
                payment = result.scalars().first()
                return payment
            
    async def add_subscription(
            self, 
            telegram_id: int, 
            subscription_type: str, 
            subscription_end: str, 
            subscription_price: float,
        ):
        async with get_session() as session:
            async with session.begin():
                subscription = Subscription(telegram_id=telegram_id, subscription_type=subscription_type, subscription_end=subscription_end, subscription_price=subscription_price)
                session.add(subscription)
                try:
                    await session.commit()
                except IntegrityError:
                    await session.rollback()
                    return None
                return subscription
    
    async def get_expired_subscriptions(self):
        async with get_session() as session:
            async with session.begin():
                query = select(Subscription).where(Subscription.subscription_end < datetime.datetime.now(), Subscription.isActive == True)
                result = await session.execute(query)
                subscriptions = result.scalars().all()
                return subscriptions
            
    async def update_subscription(self, subscription_id: int, **kwargs):
        async with get_session() as session:
            try:
                result = await session.execute(
                    select(Subscription).where(Subscription.id == subscription_id)
                )
                user = result.scalars().first()

                if not user:
                    logger.warning(f"{subscription_id} not found in update_subscription.")
                    return

                for key, value in kwargs.items():
                    if hasattr(user, key):
                        setattr(user, key, value)

                try:
                    session.add(user)
                    await session.commit()
                    logger.info(f"{subscription_id} successfully updated.")
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
                logger.error(f"Error in update_subscription: {e}")
                raise

    async def get_subscriptions_to_notify(self, time_left: datetime.timedelta):
        target_time = datetime.datetime.now() + time_left
        async with get_session() as session:
            async with session.begin():
                query = select(Subscription).where(
                    Subscription.subscription_end <= target_time,
                    Subscription.subscription_end > datetime.datetime.now(),
                    Subscription.isActive == True
                )

                result = await session.execute(query)
                subscriptions = result.scalars().all()
                
                if time_left == datetime.timedelta(days=1):
                    subscriptions = [sub for sub in subscriptions if sub.subscription_end - datetime.datetime.now() >= datetime.timedelta(days=1)]
                    
                return subscriptions
            
    async def get_active_subscription(self, telegram_id: int):
        async with get_session() as session:
            async with session.begin():
                query = select(Subscription).where(Subscription.telegram_id == telegram_id, Subscription.isActive == True)
                result = await session.execute(query)
                subscription = result.scalars().first()
                return subscription
    

    
subscription_service = SubscriptionService()