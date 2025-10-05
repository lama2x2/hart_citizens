from django.urls import path
from . import views

app_name = 'action_logs'

urlpatterns = [
    # Панель управления логами (только для администраторов)
    path('dashboard/', views.logs_dashboard, name='logs_dashboard'),
    
    # Экспорт логов
    path('export/', views.export_logs, name='export_logs'),
    
    # Логи пользователя
    path('user/', views.user_logs, name='user_logs'),
    
    # Логи королевства
    path('kingdom/', views.kingdom_logs, name='kingdom_logs'),
    
    # Статистика логов
    path('statistics/', views.logs_statistics, name='logs_statistics'),
]
