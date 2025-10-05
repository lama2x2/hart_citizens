from rest_framework import serializers
from ..models import ActionLog


class ActionLogSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ActionLog"""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_role = serializers.CharField(source='user.get_role_display', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    
    class Meta:
        model = ActionLog
        fields = [
            'id', 'user', 'user_name', 'user_email', 'user_role',
            'action', 'action_display', 'description', 'metadata',
            'ip_address', 'user_agent', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
