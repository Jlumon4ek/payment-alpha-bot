import asyncio
import datetime
from infrastructure.celery.app import celery_app
from aiogram import Bot
from core.config import settings
from application.services.subscription import SubscriptionService
from presentation.keyboards.subscription import SubscriptionKeyboard

subscription_service = SubscriptionService()
subscription_keyboard = SubscriptionKeyboard()
bot = Bot(token=settings.TOKEN)

class SubscriptionTasks:
    @staticmethod
    async def kick_expired_users():
        subscriptions = await subscription_service.get_expired_subscriptions()

        for subscription in subscriptions:
            await bot.ban_chat_member(
                chat_id=settings.CHANNEL_ID, 
                user_id=subscription.telegram_id
            )
            await subscription_service.update_subscription(
                subscription_id=subscription.id,
                isActive=False
            )

    @staticmethod
    async def notify_before_expiration(hours: int):
        time_left = datetime.timedelta(hours=hours)
        subscriptions = await subscription_service.get_subscriptions_to_notify(time_left=time_left)

        for subscription in subscriptions:
            if hours == 24:
                if subscription.subscription_end - datetime.datetime.now() >= datetime.timedelta(days=1):
                    message = "Вашу подписку осталось 24 часа. Пожалуйста, продлите подписку вовремя!"
            else:
                message = "Ваша подписка истекает через 1 час. Пожалуйста, продлите подписку!"

            await bot.send_message(
                chat_id=subscription.telegram_id,
                text=message,
                reply_markup=await subscription_keyboard.update_subscription()
            )

@celery_app.task(name="check_subscriptions")
def kick_user():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(SubscriptionTasks.kick_expired_users())

@celery_app.task(name="notify_24_hours_before_expiration")
def notify_24_hours_before_expiration():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(SubscriptionTasks.notify_before_expiration(hours=24))

@celery_app.task(name="notify_1_hour_before_expiration")
def notify_1_hour_before_expiration():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(SubscriptionTasks.notify_before_expiration(hours=1))