from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Habit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='habits')
    place = models.CharField(max_length=200, blank=True)
    time = models.TimeField()
    action = models.CharField(max_length=300)
    is_pleasant = models.BooleanField(default=False)
    related_habit = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='dependent_habits'
    )
    frequency_days = models.PositiveSmallIntegerField(default=1)
    reward = models.CharField(max_length=300, blank=True, null=True)
    estimated_time_seconds = models.PositiveSmallIntegerField(default=60)
    is_public = models.BooleanField(default=False)
    last_completed = models.DateTimeField(null=True, blank=True)
    last_reminded = models.DateTimeField(null=True, blank=True)          # ← НОВОЕ ПОЛЕ
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        # Нельзя одновременно указывать related_habit и reward
        if self.related_habit and self.reward:
            raise ValidationError(
                'Нельзя одновременно указывать связанную привычку и вознаграждение'
            )

        # related_habit может ссылаться только на привычки где is_pleasant=True
        if self.related_habit and not self.related_habit.is_pleasant:
            raise ValidationError(
                'Связанная привычка должна быть приятной (is_pleasant=True)'
            )

        # Если is_pleasant=True, то related_habit и reward должны быть пустыми
        if self.is_pleasant and (self.related_habit or self.reward):
            raise ValidationError(
                'Приятная привычка не может иметь связанную привычку или вознаграждение'
            )

        # estimated_time_seconds ≤ 120
        if self.estimated_time_seconds > 120:
            raise ValidationError(
                'Время выполнения не может превышать 120 секунд'
            )

        # frequency_days от 1 до 7 включительно
        if self.frequency_days < 1 or self.frequency_days > 7:
            raise ValidationError(
                'Частота выполнения должна быть от 1 до 7 дней'
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.action} ({self.user.username})'

    class Meta:
        ordering = ['-created_at']