from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import ActionLog


class ActionLogResource(resources.ModelResource):
    """Ресурс для импорта/экспорта логов"""
    
    class Meta:
        model = ActionLog
        fields = ('id', 'user__email', 'action', 'description', 'ip_address', 'created_at')


@admin.register(ActionLog)
class ActionLogAdmin(ImportExportModelAdmin):
    """Админка для модели ActionLog"""
    
    resource_class = ActionLogResource
    list_display = ('user_name', 'action_display', 'description_short', 'ip_address', 'created_at')
    list_filter = ('action', 'created_at', 'user__role')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'description')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at', 'metadata')
    date_hierarchy = 'created_at'
    
    def user_name(self, obj):
        """Имя пользователя"""
        return obj.user.get_full_name()
    user_name.short_description = 'Пользователь'
    
    def action_display(self, obj):
        """Отображение действия"""
        return obj.get_action_display()
    action_display.short_description = 'Действие'
    
    def description_short(self, obj):
        """Короткое описание"""
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    description_short.short_description = 'Описание'
    
    def has_add_permission(self, request):
        """Запретить добавление логов через админку"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Запретить изменение логов через админку"""
        return False
