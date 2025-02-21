from infrastructure.celery.app import celery_app
from infrastructure.celery.schedule import CELERYBEAT_SCHEDULE

celery_app.conf.beat_schedule = CELERYBEAT_SCHEDULE

if __name__ == '__main__':
    celery_app.start()  