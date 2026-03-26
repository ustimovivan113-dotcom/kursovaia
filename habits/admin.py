from django.contrib import admin
from .models import Habit


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ['action', 'user', 'time', 'is_pleasant', 'is_public', 'frequency_days']
    list_filter = ['is_pleasant', 'is_public', 'frequency_days']
    search_fields = ['action', 'user__username']
