import pytest
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import time, timedelta

from habits.models import Habit

User = get_user_model()


@pytest.fixture
def user(db):
    """Создает тестового пользователя"""
    return User.objects.create_user(
        username='testuser',
        email='test@test.com',
        password='testpass123',
        telegram_chat_id='123456789'
    )


@pytest.fixture
def pleasant_habit(db, user):
    """Создает приятную привычку"""
    return Habit.objects.create(
        user=user,
        action='Приятная привычка',
        time=time(10, 0),
        is_pleasant=True,
        place='Дом'
    )


class TestHabitModel:
    """Тесты модели Habit"""

    def test_create_habit_success(self, user):
        """Успешное создание привычки"""
        habit = Habit(
            user=user,
            action='Делать зарядку',
            time=time(8, 0),
            place='Дом',
            frequency_days=1,
            estimated_time_seconds=60
        )
        habit.save()
        
        assert habit.id is not None
        assert habit.action == 'Делать зарядку'
        assert habit.user == user

    def test_habit_with_reward(self, user):
        """Создание привычки с вознаграждением"""
        habit = Habit(
            user=user,
            action='Читать книгу',
            time=time(21, 0),
            reward='Смотреть сериал',
            frequency_days=1,
            estimated_time_seconds=30
        )
        habit.save()
        
        assert habit.reward == 'Смотреть сериал'

    def test_habit_with_related_habit(self, user, pleasant_habit):
        """Создание привычки со связанной приятной привычкой"""
        habit = Habit(
            user=user,
            action='Учиться программировать',
            time=time(19, 0),
            related_habit=pleasant_habit,
            frequency_days=1,
            estimated_time_seconds=120
        )
        habit.save()
        
        assert habit.related_habit == pleasant_habit

    def test_pleasant_habit_cannot_have_reward(self, user):
        """Приятная привычка не может иметь вознаграждение"""
        habit = Habit(
            user=user,
            action='Слушать музыку',
            time=time(15, 0),
            is_pleasant=True,
            reward='Конфетка',
            place='Дом'
        )
        
        with pytest.raises(ValidationError):
            habit.save()

    def test_pleasant_habit_cannot_have_related_habit(self, user, pleasant_habit):
        """Приятная привычка не может иметь связанную привычку"""
        pleasant_habit2 = Habit(
            user=user,
            action='Еще одна приятная',
            time=time(16, 0),
            is_pleasant=True
        )
        pleasant_habit2.save()
        
        pleasant_habit.related_habit = pleasant_habit2
        
        with pytest.raises(ValidationError):
            pleasant_habit.save()

    def test_cannot_have_both_related_habit_and_reward(self, user, pleasant_habit):
        """Нельзя одновременно указывать related_habit и reward"""
        habit = Habit(
            user=user,
            action='Тренировка',
            time=time(7, 0),
            related_habit=pleasant_habit,
            reward='Пирог',
            frequency_days=1
        )
        
        with pytest.raises(ValidationError):
            habit.save()

    def test_related_habit_must_be_pleasant(self, user):
        """Связанная привычка должна быть приятной"""
        not_pleasant = Habit.objects.create(
            user=user,
            action='Не приятная',
            time=time(12, 0),
            is_pleasant=False
        )
        
        habit = Habit(
            user=user,
            action='Работать',
            time=time(9, 0),
            related_habit=not_pleasant,
            frequency_days=1
        )
        
        with pytest.raises(ValidationError):
            habit.save()

    def test_estimated_time_cannot_exceed_120(self, user):
        """Время выполнения не может превышать 120 секунд"""
        habit = Habit(
            user=user,
            action='Долгая задача',
            time=time(10, 0),
            estimated_time_seconds=180,
            frequency_days=1
        )
        
        with pytest.raises(ValidationError):
            habit.save()

    def test_frequency_days_must_be_between_1_and_7(self, user):
        """Частота выполнения должна быть от 1 до 7 дней"""
        habit = Habit(
            user=user,
            action='Редкая привычка',
            time=time(10, 0),
            frequency_days=10,
            estimated_time_seconds=60
        )
        
        with pytest.raises(ValidationError):
            habit.save()

    def test_habit_str(self, user):
        """Тест строкового представления"""
        habit = Habit.objects.create(
            user=user,
            action='Тестовая привычка',
            time=time(10, 0),
            frequency_days=1
        )
        
        assert 'Тестовая привычка' in str(habit)
        assert 'testuser' in str(habit)


class TestHabitViewSet:
    """Тесты ViewSet привычек"""

    @pytest.fixture
    def api_client(self):
        from rest_framework.test import APIClient
        return APIClient()

    @pytest.fixture
    def authenticated_client(self, api_client, user):
        api_client.force_authenticate(user=user)
        return api_client

    def test_list_own_habits(self, authenticated_client, user):
        """Получение списка своих привычек"""
        Habit.objects.create(
            user=user,
            action='Моя привычка',
            time=time(10, 0),
            frequency_days=1
        )
        
        response = authenticated_client.get('/api/habits/')
        
        assert response.status_code == 200
        assert len(response.data['results']) == 1

    def test_cannot_list_other_user_habits(self, authenticated_client, user):
        """Нельзя получить привычки другого пользователя"""
        other_user = User.objects.create_user(
            username='other',
            password='pass123'
        )
        Habit.objects.create(
            user=other_user,
            action='Чужая привычка',
            time=time(10, 0),
            frequency_days=1
        )
        
        response = authenticated_client.get('/api/habits/')
        
        assert response.status_code == 200
        assert len(response.data['results']) == 0

    def test_create_habit(self, authenticated_client, user):
        """Создание привычки"""
        data = {
            'action': 'Новая привычка',
            'time': '08:00',
            'place': 'Дом',
            'frequency_days': 1,
            'estimated_time_seconds': 60
        }
        
        response = authenticated_client.post('/api/habits/', data)
        
        assert response.status_code == 201
        assert response.data['action'] == 'Новая привычка'

    def test_unauthenticated_cannot_create(self, api_client):
        """Неавторизованный пользователь не может создавать"""
        data = {
            'action': 'Привычка',
            'time': '08:00',
            'frequency_days': 1
        }
        
        response = api_client.post('/api/habits/', data)
        
        assert response.status_code == 401

    def test_update_own_habit(self, authenticated_client, user):
        """Изменение своей привычки"""
        habit = Habit.objects.create(
            user=user,
            action='Старое действие',
            time=time(10, 0),
            frequency_days=1
        )
        
        response = authenticated_client.patch(
            f'/api/habits/{habit.id}/',
            {'action': 'Новое действие'}
        )
        
        assert response.status_code == 200
        assert response.data['action'] == 'Новое действие'

    def test_cannot_update_other_user_habit(self, authenticated_client, user):
        """Нельзя изменить чужую привычку"""
        other_user = User.objects.create_user(
            username='other2',
            password='pass123'
        )
        habit = Habit.objects.create(
            user=other_user,
            action='Чужая',
            time=time(10, 0),
            frequency_days=1
        )
        
        response = authenticated_client.patch(
            f'/api/habits/{habit.id}/',
            {'action': 'Попытка изменить'}
        )
        
        assert response.status_code == 404


class TestPublicHabits:
    """Тесты публичных привычек"""

    @pytest.fixture
    def api_client(self):
        from rest_framework.test import APIClient
        return APIClient()

    @pytest.fixture
    def authenticated_client(self, api_client, user):
        api_client.force_authenticate(user=user)
        return api_client

    def test_list_public_habits(self, authenticated_client, user):
        """Получение списка публичных привычек"""
        Habit.objects.create(
            user=user,
            action='Публичная',
            time=time(10, 0),
            is_public=True,
            frequency_days=1
        )
        
        response = authenticated_client.get('/api/public-habits/')
        
        assert response.status_code == 200
        assert len(response.data['results']) == 1

    def test_private_habits_not_in_public_list(self, authenticated_client, user):
        """Приватные привычки не видны в публичном списке"""
        Habit.objects.create(
            user=user,
            action='Приватная',
            time=time(10, 0),
            is_public=False,
            frequency_days=1
        )
        
        response = authenticated_client.get('/api/public-habits/')
        
        assert response.status_code == 200
        assert len(response.data['results']) == 0
