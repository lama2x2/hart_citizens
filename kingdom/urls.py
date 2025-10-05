from django.urls import path
from . import views
from . import logs_views

app_name = 'kingdom'

urlpatterns = [
    # Панели управления
    path('king/dashboard/', views.KingDashboardView.as_view(), name='king_dashboard'),
    path('citizen/dashboard/', views.CitizenDashboardView.as_view(), name='citizen_dashboard'),
    
    # Тестирование
    path('test/', views.TestView.as_view(), name='test'),
    path('test/start/', views.start_test, name='start_test'),
    path('test/question/<uuid:question_id>/answer/', views.answer_question, name='answer_question'),
    path('test/results/<uuid:pk>/', views.CitizenTestResultsView.as_view(), name='test_results'),
    
    # Управление подданными (для королей)
    path('citizen/<uuid:citizen_id>/enroll/', views.enroll_citizen, name='enroll_citizen'),
    path('citizen/<uuid:pk>/details/', views.KingCitizenDetailsView.as_view(), name='citizen_details'),
    
    # Логи
    path('logs/', logs_views.user_logs, name='user_logs'),
    path('logs/kingdom/', logs_views.kingdom_logs, name='kingdom_logs'),
    path('logs/export/', logs_views.export_logs, name='export_logs'),
    path('logs/statistics/', logs_views.logs_statistics, name='logs_statistics'),
]
