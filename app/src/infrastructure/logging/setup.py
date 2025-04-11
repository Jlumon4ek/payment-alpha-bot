import logging
import sentry_sdk
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.aiohttp import AioHttpIntegration
import logging
from aiogram import Bot, Dispatcher
from aiogram import BaseMiddleware
from typing import Dict, Any, Callable, Awaitable

def setup_logging():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    return logger


def setup_sentry(dsn: str, environment: str = "production"):
    logging_integration = LoggingIntegration(
        level=logging.INFO,
        event_level=logging.ERROR
    )
    
    def before_send(event, hint):
        return event
    
    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        integrations=[
            logging_integration,
            SqlalchemyIntegration(),
            AioHttpIntegration(),
        ],
        traces_sample_rate=1.0,
        send_default_pii=True,
        before_send=before_send
    )
    
    logging.info("Sentry initialized")
    
    class SentryContextMiddleware(BaseMiddleware):
        async def __call__(
            self,
            handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
            event: Any,
            data: Dict[str, Any]
        ) -> Any:
            if "event_from_user" in data:
                user = data["event_from_user"]
                with sentry_sdk.configure_scope() as scope:
                    scope.set_user({
                        "id": user.id,
                        "username": user.username,
                        "first_name": user.first_name,
                        "last_name": user.last_name
                    })
            
            if "event_message" in data:
                message = data["event_message"]
                with sentry_sdk.configure_scope() as scope:
                    scope.set_context("message", {
                        "message_id": message.message_id,
                        "chat_id": message.chat.id,
                        "chat_type": message.chat.type,
                        "text": message.text if hasattr(message, "text") else None
                    })
            
            if "event_update" in data:
                with sentry_sdk.configure_scope() as scope:
                    scope.set_context("telegram_update", 
                                    data["event_update"].model_dump())
            
            try:
                return await handler(event, data)
            except Exception as e:
                sentry_sdk.capture_exception(e)
                raise
    
    return SentryContextMiddleware()