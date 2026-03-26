from rest_framework import serializers
from .models import Habit


class HabitSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Habit
        fields = [
            'id', 'user', 'place', 'time', 'action', 'is_pleasant',
            'related_habit', 'frequency_days', 'reward',
            'estimated_time_seconds', 'is_public', 'last_completed',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'last_completed']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def validate(self, attrs):
        # Дополнительная валидация для related_habit
        related_habit = attrs.get('related_habit')
        if related_habit:
            if not related_habit.is_pleasant:
                raise serializers.ValidationError({
                    'related_habit': 'Связанная привычка должна быть приятной (is_pleasant=True)'
                })
        return attrs

    def validate_estimated_time_seconds(self, value):
        if value > 120:
            raise serializers.ValidationError('Время выполнения не может превышать 120 секунд')
        return value


class HabitListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка привычек (без related_habit для избежания рекурсии)"""
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Habit
        fields = [
            'id', 'user', 'place', 'time', 'action', 'is_pleasant',
            'frequency_days', 'estimated_time_seconds', 'is_public',
            'created_at'
        ]
        read_only_fields = fields