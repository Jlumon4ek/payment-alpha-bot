import logging
import datetime
from sqlalchemy import select
from domain.models.subscription import Subscription
from domain.models.payment import Payment
from .base import BaseService

logger = logging.getLogger(__name__)

class PaymentService(BaseService):
    def __init__(self):
        super().__init__(Payment)

    async def get_by_receipt_id(self, receipt_id: str):
        return await self.get_by_field('receipt_id', receipt_id)

class SubscriptionService(BaseService):
    def __init__(self):
        super().__init__(Subscription)
        self.payment_service = PaymentService()

    async def get_subscription_by_telegram_id(self, telegram_id: int):
        async def operation(session):
            query = select(self.model)\
                .where(self.model.telegram_id == telegram_id)\
                .order_by(self.model.subscription_end.desc())
            result = await session.execute(query)
            return result.scalars().first()
            
        return await self._execute_with_session(operation)

    async def get_subscriptions(self):
        async def operation(session):
            query = select(self.model).where(
                self.model.isActive == True
            )
            result = await session.execute(query)
            subscriptions = result.scalars().all()
            logger.info(f"Found {len(subscriptions)} expired subscriptions")
            return subscriptions
        return await self._execute_with_session(operation)

    async def add_payment(
        self,
        telegram_id: int,
        receipt_id: str,
        full_name: str,
        passport_id: str,
        price: float,
        payment_date: datetime.datetime
    ):
        logger.info(f"Adding payment for user {telegram_id}, receipt {receipt_id}")
        return await self.payment_service.create(
            telegram_id=telegram_id,
            receipt_id=receipt_id,
            full_name=full_name,
            passport_id=passport_id,
            price=price,
            payment_date=payment_date
        )

    async def get_expired_subscriptions(self):
        async def operation(session):
            query = select(self.model).where(
                self.model.subscription_end < datetime.datetime.now(),
                self.model.isActive == True
            )
            result = await session.execute(query)
            subscriptions = result.scalars().all()
            logger.info(f"Found {len(subscriptions)} expired subscriptions")
            return subscriptions
        return await self._execute_with_session(operation)

    async def get_subscriptions_to_notify(self, time_left: datetime.timedelta):
        target_time = datetime.datetime.now() + time_left
        async def operation(session):
            query = select(self.model).where(
                self.model.subscription_end <= target_time,
                self.model.subscription_end > datetime.datetime.now(),
                self.model.isActive == True
            )
            result = await session.execute(query)
            subscriptions = result.scalars().all()
            
            if time_left == datetime.timedelta(days=1):
                subscriptions = [
                    sub for sub in subscriptions 
                    if sub.subscription_end - datetime.datetime.now() >= datetime.timedelta(days=1)
                ]
            
            logger.info(
                f"Found {len(subscriptions)} subscriptions to notify "
                f"for time left: {time_left}"
            )
            return subscriptions
        return await self._execute_with_session(operation)

    async def get_active_subscription(self, telegram_id: int):
        subscription = await self.get_by_field('telegram_id', telegram_id)
        if subscription:
            logger.debug(f"Found active subscription for user {telegram_id}")
        else:
            logger.debug(f"No active subscription found for user {telegram_id}")
        return subscription
    
    