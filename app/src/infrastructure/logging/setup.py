import logging
import sentry_sdk
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.aiohttp import AioHttpIntegration
import logging


def setup_logging():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    return logger

def setup_sentry(dsn: str, environment: str = "production"):
    logging_integration = LoggingIntegration(
        level=logging.INFO,        # Уровень для захвата в Sentry
        event_level=logging.ERROR  # Ошибки и выше отправляются как события
    )
    
    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        integrations=[
            logging_integration,
            SqlalchemyIntegration(),  # Для отслеживания запросов к БД
            AioHttpIntegration(),     # Для работы с aiohttp (используется в aiogram)
        ],
        # Добавляем информацию о пользователе бота в события
        send_default_pii=True
    )
    
    logging.info("Sentry initialized")