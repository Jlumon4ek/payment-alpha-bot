import asyncio
import datetime
import os
from celery import Celery
from aiogram import (
    Bot
)
from config import settings
from bot.subscription.service import subscription_service
from celery.schedules import crontab
from bot.subscription.keyboard import subscription_keyboard

bot = Bot(token=settings.TOKEN)

os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')

broker_url = settings.REDIS
app  = Celery(
    "tasks",
    broker=broker_url
)


@app.task(name="check_subscriptions")
def kick_user():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(async_kick_user())


@app.task(name="notify_24_hours_before_expiration")
def notify_24_hours_before_expiration():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(async_notify_24_hours_before_expiration())


@app.task(name="notify_1_hour_before_expiration")
def notify_1_hour_before_expiration():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(async_notify_1_hour_before_expiration())


async def async_kick_user():
    subscriptions = await subscription_service.get_expired_subscriptions()

    for subscription in subscriptions:
        await bot.ban_chat_member(chat_id=settings.CHANNEL_ID, user_id=subscription.telegram_id)
        await subscription_service.update_subscription(
            subscription_id = subscription.id,
            isActive = False
        )

async def async_notify_24_hours_before_expiration():
    subscriptions = await subscription_service.get_subscriptions_to_notify(time_left=datetime.timedelta(days=1))

    for subscription in subscriptions:
        if subscription.subscription_end - datetime.datetime.now() >= datetime.timedelta(days=1):
            await bot.send_message(
                chat_id=subscription.telegram_id,
                text="Вашу подписку осталось 24 часа. Пожалуйста, продлите подписку вовремя!",
                reply_markup=await subscription_keyboard.update_subscription()
            )

async def async_notify_1_hour_before_expiration():
    subscriptions = await subscription_service.get_subscriptions_to_notify(time_left=datetime.timedelta(hours=1))

    for subscription in subscriptions:
        await bot.send_message(
            chat_id=subscription.telegram_id,
            text="Ваша подписка истекает через 1 час. Пожалуйста, продлите подписку!",
            reply_markup=await subscription_keyboard.update_subscription()

        )


app.conf.beat_schedule = {
    'check-subscriptions': {
        'task': 'check_subscriptions',
        'schedule': datetime.timedelta(seconds=2), 
        # 'schedule': crontab(minute='*/30'),
    },
    'notify-24-hours-before-expiration': {
        'task': 'notify_24_hours_before_expiration',
        'schedule': crontab(minute=0, hour='*'),
        # 'schedule': datetime.timedelta(seconds=2), 
    },
    'notify-1-hour-before-expiration': {
        'task': 'notify_1_hour_before_expiration',
        'schedule': crontab(minute=0, hour='*'),
        # 'schedule': datetime.timedelta(seconds=2), /
    },
}

app.conf.timezone = 'UTC'





