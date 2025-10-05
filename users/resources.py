from import_export import resources
from .models import User


class UserResource(resources.ModelResource):
    """Ресурс для импорта/экспорта пользователей"""
    
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff', 'date_joined', 'last_login')
        export_order = ('id', 'email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff', 'date_joined', 'last_login')
