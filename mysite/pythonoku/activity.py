from datetime import timedelta

from django.utils import timezone

from .models import UserProfile
from .notifications import queue_notification

STREAK_MILESTONES = {1, 3, 7, 14, 30, 60, 100}


def touch_learning_streak(user, reason='activity'):
    if not user or not getattr(user, 'is_authenticated', False):
        return None, False
    if user.is_admin or user.is_staff or user.is_superuser:
        return getattr(user, 'streak', 0), False

    today = timezone.localdate()
    last_activity = getattr(user, 'last_activity', None)

    if last_activity == today:
        return user.streak, False

    if last_activity is None and (user.streak or 0) > 0:
        new_streak = user.streak + 1
    elif last_activity == today - timedelta(days=1):
        new_streak = (user.streak or 0) + 1
    else:
        new_streak = 1

    UserProfile.objects.filter(pk=user.pk).update(
        streak=new_streak,
        last_activity=today,
    )

    user.streak = new_streak
    user.last_activity = today

    if new_streak in STREAK_MILESTONES:
        if new_streak == 1:
            title = 'Серия началась 🔥'
            text = 'Ты сделал учебное действие сегодня. Возвращайся завтра, чтобы продолжить серию.'
        else:
            title = f'Серия {new_streak} дней 🔥'
            text = f'Отличный ритм: ты занимаешься уже {new_streak} дней подряд.'

        queue_notification(user.pk, 'achievement', title, text)

    return new_streak, True
