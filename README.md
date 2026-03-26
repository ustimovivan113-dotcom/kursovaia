# Трекер полезных привычек (Backend)

Backend-часть SPA-приложения для трекера полезных привычек на основе книги Джеймса Клира «Атомные привычки».

## Технологии

- **Python** 3.11
- **Django** 4.2.7
- **Django REST Framework**
- **Djoser + SimpleJWT** — аутентификация
- **Celery + Redis** — отложенные задачи
- **django-celery-beat** — планировщик
- **SQLite** (для разработки)
- **Telegram Bot API** — отправка напоминаний

## Основные возможности

- Регистрация и JWT-авторизация
- CRUD привычек (только свои)
- Публичный список привычек (только чтение)
- Валидация по ТЗ:
  - время выполнения ≤ 120 секунд
  - нельзя одновременно указывать `reward` и `related_habit`
  - связанные привычки могут быть только приятными
  - частота от 1 до 7 дней
- Пагинация (5 привычек на страницу)
- Отложенные напоминания в Telegram через Celery

## Запуск проекта

### 1. Клонирование и установка

```bash
git clone https://github.com/ustimovivan113-dotcom/kursovaia.git
cd kursovaia
python -m venv venv
venv\Scripts\activate    # Windows
pip install -r requirements.txt