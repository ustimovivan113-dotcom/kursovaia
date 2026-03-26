import requests
from django.conf import settings


def send_telegram_message(chat_id, message):
    """
    Отправляет сообщение в Telegram.
    
    Args:
        chat_id: ID чата пользователя в Telegram
        message: Текст сообщения
    
    Returns:
        True если сообщение отправлено, False в противном случае
    """
    token = settings.TELEGRAM_BOT_TOKEN
    
    if not token:
        print('TELEGRAM_BOT_TOKEN не настроен')
        return False
    
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    data = {
        'chat_id': chat_id,
        'text': message,
    }
    
    try:
        response = requests.post(url, data=data, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f'Ошибка отправки в Telegram: {e}')
        return False


def format_habit_notification(habit):
    """
    Формирует текст уведомления о привычке.
    
    Args:
        habit: Объект модели Habit
    
    Returns:
        Отформатированная строка сообщения
    """
    place = habit.place if habit.place else 'место не указано'
    time = habit.time.strftime('%H:%M')
    action = habit.action
    
    return f'Пора выполнять привычку: {action} в {place} в {time}'
