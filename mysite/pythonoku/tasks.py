import logging

logger = logging.getLogger(__name__)

try:
    from celery import shared_task
except Exception:  # Celery is optional for local development.
    class _LocalTask:
        def __init__(self, func):
            self.func = func
            self.__name__ = getattr(func, '__name__', 'local_task')

        def __call__(self, *args, **kwargs):
            return self.func(*args, **kwargs)

        def delay(self, *args, **kwargs):
            return self.func(*args, **kwargs)

    def shared_task(*decorator_args, **decorator_kwargs):
        if decorator_args and callable(decorator_args[0]):
            return _LocalTask(decorator_args[0])

        def decorator(func):
            return _LocalTask(func)

        return decorator


@shared_task(ignore_result=True)
def create_notification_task(user_id, notification_type, title, text):
    from .models import Notification, UserProfile

    user = UserProfile.objects.filter(pk=user_id).first()
    if not user:
        logger.warning('Notification skipped: user %s was not found', user_id)
        return None

    notification = Notification.objects.create(
        user=user,
        type=notification_type,
        title=title,
        text=text,
    )
    return notification.pk
