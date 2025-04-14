from celery.schedules import crontab

CELERYBEAT_SCHEDULE = {
    'check-subscriptions': {
        'task': 'src.application.tasks.subscription.check_subscriptions',
        'schedule': crontab(minute='*/1'),  
    },
}