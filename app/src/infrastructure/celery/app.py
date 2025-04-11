from celery import Celery
from core.config import settings
import os
from sentry_sdk.integrations.celery import CeleryIntegration
import sentry_sdk

os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')

def create_celery_app() -> Celery:
    if settings.SENTRY_DSN and not sentry_sdk.Hub.current.client:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            integrations=[CeleryIntegration()],
            traces_sample_rate=1.0
        )

    
    app = Celery(
        "tasks",
        broker=settings.RABBITMQ_URL,
    )
    
    app.conf.timezone = 'UTC'
    return app

celery_app = create_celery_app()