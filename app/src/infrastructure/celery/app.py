from celery import Celery
from core.config import settings
import os

os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')

def create_celery_app() -> Celery:
    app = Celery(
        "tasks",
        broker=settings.RABBITMQ_URL,
    )
    
    app.conf.timezone = 'UTC'
    return app

celery_app = create_celery_app()