from django.db.models import Count
from kingdom.models import Kingdom, King, Citizen, Test
from action_logs.models import ActionLog
from users.models import User


def admin_dashboard_context(request):
    """Контекстный процессор для главной страницы админки"""
    if request.path == '/admin/' and request.user.is_staff:
        return {
            'total_users': User.objects.count(),
            'total_kingdoms': Kingdom.objects.count(),
            'total_kings': King.objects.count(),
            'total_citizens': Citizen.objects.count(),
            'total_tests': Test.objects.count(),
            'total_logs': ActionLog.objects.count(),
            'recent_logs': ActionLog.objects.select_related('user').order_by('-created_at')[:10],
        }
    return {}
