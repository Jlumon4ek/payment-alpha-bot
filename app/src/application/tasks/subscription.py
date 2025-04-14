import asyncio
import datetime
import logging

import sentry_sdk
from infrastructure.celery.app import celery_app
from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramAPIError
from core.config import settings
from application.services.subscription import SubscriptionService
from presentation.keyboards.subscription import SubscriptionKeyboard

subscription_service = SubscriptionService()
subscription_keyboard = SubscriptionKeyboard()
bot = Bot(token=settings.TOKEN)

class SubscriptionTasks:
    @staticmethod
    async def check_subscriptions():
        try:
            subscriptions = await subscription_service.get_subscriptions()
            now = datetime.datetime.now()

            for subscription in subscriptions:
                try:
                    if (
                        not subscription.notified_24
                        and subscription.subscription_end <= (now + datetime.timedelta(hours=24))
                        and subscription.subscription_end > now
                    ):
                        await bot.send_message(
                            chat_id=subscription.telegram_id,
                            text="Вашу подписку осталось 24 часа. Пожалуйста, продлите подписку вовремя!",
                            reply_markup=await subscription_keyboard.update_subscription(),
                        )
                        await subscription_service.update(
                            field_name="id", field_value=subscription.id, notified_24=True
                        )
                        logging.info(f"Отправлено уведомление за 24 часа пользователю {subscription.telegram_id}")

                    if (
                        not subscription.notified_1
                        and subscription.subscription_end <= (now + datetime.timedelta(hours=1))
                        and subscription.subscription_end > now
                    ):
                        await bot.send_message(
                            chat_id=subscription.telegram_id,
                            text="Ваша подписка истекает через 1 час. Пожалуйста, продлите подписку!",
                            reply_markup=await subscription_keyboard.update_subscription(),
                        )
                        await subscription_service.update(
                            field_name="id", field_value=subscription.id, notified_1=True
                        )
                        logging.info(f"Отправлено уведомление за 1 час пользователю {subscription.telegram_id}")

                    if subscription.subscription_end <= now:
                        try:
                            await bot.ban_chat_member(
                                chat_id=settings.CHANNEL_ID, user_id=subscription.telegram_id
                            )

                            logging.info(f"Пользователь {subscription.telegram_id} заблокирован в канале {settings.CHANNEL_ID}")
                        except TelegramForbiddenError:
                            sentry_sdk.capture_exception(e)

                        except TelegramAPIError as e:
                            sentry_sdk.capture_exception(e)

                        try:
                            await bot.ban_chat_member(
                                chat_id=settings.DISCUSSION_GROUP_ID, user_id=subscription.telegram_id
                            )
                            logging.info(f"Пользователь {subscription.telegram_id} заблокирован в группе {settings.DISCUSSION_GROUP_ID}")
                        except TelegramForbiddenError:
                            sentry_sdk.capture_exception(e)
                        except TelegramAPIError as e:
                            sentry_sdk.capture_exception(e)

                        await subscription_service.update(
                            field_name="id", field_value=subscription.id, isActive=False
                        )
                        logging.info(f"Подписка пользователя {subscription.telegram_id} деактивирована.")

                except TelegramForbiddenError:
                    logging.warning(f"Пользователь {subscription.telegram_id} заблокировал бота или удалил чат.")
                except TelegramAPIError as e:
                    sentry_sdk.capture_exception(e)
                except Exception as e:
                    sentry_sdk.capture_exception(e)

        except Exception as e:
            sentry_sdk.capture_exception(e)

@celery_app.task(name="src.application.tasks.subscription.check_subscriptions")
def check_subscriptions():
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(SubscriptionTasks.check_subscriptions())
    except Exception as e:
        logging.critical(f"Ошибка выполнения Celery-задачи check_subscriptions: {e}")