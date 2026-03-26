from rest_framework import viewsets, permissions
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from .models import Habit
from .serializers import HabitSerializer, HabitListSerializer
from .permissions import IsOwner, IsOwnerOrReadOnly


class HabitPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 10


class HabitViewSet(viewsets.ModelViewSet):
    """ViewSet для управления привычками пользователя"""
    serializer_class = HabitSerializer
    pagination_class = HabitPagination
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        """Возвращает только привычки текущего пользователя"""
        return Habit.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return HabitListSerializer
        return HabitSerializer

    def perform_create(self, serializer):
        """При создании автоматически устанавливаем текущего пользователя"""
        serializer.save(user=self.request.user)


class PublicHabitViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для просмотра публичных привычек всех пользователей"""
    serializer_class = HabitListSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = HabitPagination

    def get_queryset(self):
        """Возвращает только публичные привычки"""
        return Habit.objects.filter(is_public=True).select_related('user')
