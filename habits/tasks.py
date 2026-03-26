from celery import shared_task
from django.utils import timezone
from .models import Habit
from .telegram_service import send_telegram_message, format_habit_notification


@shared_task
def check_habits():
    """
    Проверяет каждую минуту, нужно ли отправить напоминание о привычке.
    Учитывает frequency_days и время последнего напоминания.
    Запускается каждые 60 секунд через celery beat.
    """
    now = timezone.now()
    today = now.date()
    current_time = now.time()

    # Находим привычки, время которых уже наступило сегодня (или раньше в этот день)
    habits = Habit.objects.filter(
        time__lte=current_time
    ).select_related('user')

    for habit in habits:
        if not habit.user.telegram_chat_id:
            continue

        # Проверяем, когда в последний раз отправляли напоминание
        should_send = False

        if habit.last_reminded:
            days_since_reminded = (today - habit.last_reminded.date()).days
            if days_since_reminded >= habit.frequency_days:
                should_send = True
        else:
            # Никогда не напоминали → отправляем, если время пришло
            should_send = True

        if should_send:
            message = format_habit_notification(habit)
            success = send_telegram_message(habit.user.telegram_chat_id, message)

            if success:
                habit.last_reminded = now
                habit.save(update_fields=['last_reminded'])