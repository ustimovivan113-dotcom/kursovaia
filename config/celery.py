# config/celery.py

import os
from celery import Celery

# Устанавливаем переменную окружения DJANGO_SETTINGS_MODULE, если она ещё не установлена
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('habit_tracker')  # имя приложения, можно оставить как есть или поменять на project_name

# Загружаем настройки из settings.py с префиксом CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически находим задачи в приложениях (tasks.py)
app.autodiscover_tasks()