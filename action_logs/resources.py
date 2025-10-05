from import_export import resources
from .models import ActionLog


class ActionLogResource(resources.ModelResource):
    """Ресурс для импорта/экспорта логов"""
    
    class Meta:
        model = ActionLog
        fields = ('id', 'user__email', 'action', 'description', 'ip_address', 'created_at')
        export_order = ('id', 'user__email', 'action', 'description', 'ip_address', 'created_at')
