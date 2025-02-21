from celery.schedules import crontab

CELERYBEAT_SCHEDULE = {
    'check-subscriptions': {
        'task': 'check_subscriptions',
        'schedule': crontab(minute='*/30'),
    },
    'notify-24-hours-before-expiration': {
        'task': 'notify_24_hours_before_expiration',
        'schedule': crontab(minute='*/30'),
    },
    'notify-1-hour-before-expiration': {
        'task': 'notify_1_hour_before_expiration',
        'schedule': crontab(minute='*/30'),
    },
}