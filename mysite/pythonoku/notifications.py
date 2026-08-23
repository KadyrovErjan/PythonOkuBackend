import logging

from django.conf import settings
from django.db import transaction

from .models import Notification

logger = logging.getLogger(__name__)


def create_notification_now(user_id, notification_type, title, text):
    if not user_id:
        return None

    return Notification.objects.create(
        user_id=user_id,
        type=notification_type,
        title=title,
        text=text,
    )


def queue_notification(user_or_id, notification_type='system', title='', text=''):
    user_id = getattr(user_or_id, 'pk', user_or_id)
    if not user_id:
        return

    def dispatch():
        if getattr(settings, 'NOTIFICATIONS_USE_CELERY', True):
            try:
                from .tasks import create_notification_task
                create_notification_task.delay(user_id, notification_type, title, text)
                return
            except Exception:
                logger.exception('Celery notification dispatch failed; falling back to direct create.')

        create_notification_now(user_id, notification_type, title, text)

    transaction.on_commit(dispatch)


def queue_notifications(user_ids, notification_type='system', title='', text=''):
    for user_id in set(filter(None, user_ids)):
        queue_notification(user_id, notification_type, title, text)
