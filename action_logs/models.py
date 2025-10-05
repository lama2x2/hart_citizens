import uuid
from django.db import models
from django.conf import settings


class ActionLog(models.Model):
    """Модель лога действий"""
    
    ACTION_CHOICES = [
        ('login', 'Вход в систему'),
        ('logout', 'Выход из системы'),
        ('register', 'Регистрация'),
        ('test_start', 'Начало тестирования'),
        ('test_complete', 'Завершение тестирования'),
        ('enrollment', 'Зачисление подданного'),
        ('test_pass', 'Прохождение теста'),
        ('test_fail', 'Неудачное прохождение теста'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='action_logs'
    )
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        verbose_name='Действие'
    )
    description = models.TextField(blank=True, verbose_name='Описание')
    metadata = models.JSONField(default=dict, blank=True, verbose_name='Метаданные')
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name='IP адрес')
    user_agent = models.TextField(blank=True, null=True, verbose_name='User Agent')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    class Meta:
        verbose_name = 'Лог действия'
        verbose_name_plural = 'Логи действий'
        db_table = 'action_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'action']),
            models.Index(fields=['created_at']),
            models.Index(fields=['action']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_action_display()} ({self.created_at.strftime('%d.%m.%Y %H:%M')})"
