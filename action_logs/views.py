from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta
import logging

from .models import ActionLog
from .utils import export_logs_to_excel, get_user_activity_logs, get_kingdom_activity_logs

logger = logging.getLogger('action_logs')


@staff_member_required
def logs_dashboard(request):
    """Панель управления логами для администраторов"""
    # Получаем параметры фильтрации
    action_filter = request.GET.get('action', '')
    user_filter = request.GET.get('user', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Базовый queryset
    logs = ActionLog.objects.all().select_related('user').order_by('-created_at')
    
    # Применяем фильтры
    if action_filter:
        logs = logs.filter(action=action_filter)
    
    if user_filter:
        logs = logs.filter(
            Q(user__first_name__icontains=user_filter) |
            Q(user__last_name__icontains=user_filter) |
            Q(user__email__icontains=user_filter)
        )
    
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            logs = logs.filter(created_at__date__gte=date_from_obj)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            logs = logs.filter(created_at__date__lte=date_to_obj)
        except ValueError:
            pass
    
    # Пагинация
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Статистика
    total_logs = ActionLog.objects.count()
    today_logs = ActionLog.objects.filter(created_at__date=timezone.now().date()).count()
    week_logs = ActionLog.objects.filter(
        created_at__date__gte=timezone.now().date() - timedelta(days=7)
    ).count()
    
    # Топ действий
    top_actions = ActionLog.objects.values('action').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    context = {
        'page_obj': page_obj,
        'total_logs': total_logs,
        'today_logs': today_logs,
        'week_logs': week_logs,
        'top_actions': top_actions,
        'action_choices': ActionLog.ACTION_CHOICES,
        'action_filter': action_filter,
        'user_filter': user_filter,
        'date_from': date_from,
        'date_to': date_to,
    }
    
    return render(request, 'action_logs/logs_dashboard.html', context)


@staff_member_required
def export_logs(request):
    """Экспорт логов в Excel"""
    try:
        # Получаем параметры фильтрации (те же, что и в dashboard)
        action_filter = request.GET.get('action', '')
        user_filter = request.GET.get('user', '')
        date_from = request.GET.get('date_from', '')
        date_to = request.GET.get('date_to', '')
        
        # Базовый queryset
        logs = ActionLog.objects.all().select_related('user').order_by('-created_at')
        
        # Применяем фильтры
        if action_filter:
            logs = logs.filter(action=action_filter)
        
        if user_filter:
            logs = logs.filter(
                Q(user__first_name__icontains=user_filter) |
                Q(user__last_name__icontains=user_filter) |
                Q(user__email__icontains=user_filter)
            )
        
        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
                logs = logs.filter(created_at__date__gte=date_from_obj)
            except ValueError:
                pass
        
        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
                logs = logs.filter(created_at__date__lte=date_to_obj)
            except ValueError:
                pass
        
        # Ограничиваем количество записей для экспорта
        logs = logs[:10000]  # Максимум 10000 записей
        
        # Генерируем имя файла
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        filename = f'action_logs_{timestamp}.xlsx'
        
        # Экспортируем в Excel
        response = export_logs_to_excel(logs, filename)
        
        if response:
            return response
        else:
            return JsonResponse({'error': 'Ошибка при экспорте логов'}, status=500)
    
    except Exception as e:
        logger.error(f'Ошибка при экспорте логов: {str(e)}')
        return JsonResponse({'error': 'Внутренняя ошибка сервера'}, status=500)


@login_required
def user_logs(request):
    """Логи активности текущего пользователя"""
    logs = get_user_activity_logs(request.user)
    
    # Пагинация
    paginator = Paginator(logs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'user': request.user,
    }
    
    return render(request, 'action_logs/user_logs.html', context)


@login_required
def kingdom_logs(request):
    """Логи активности по королевству пользователя"""
    if request.user.is_king:
        kingdom = request.user.king_profile.kingdom
    elif request.user.is_citizen:
        kingdom = request.user.citizen_profile.kingdom
    else:
        return JsonResponse({'error': 'Недостаточно прав'}, status=403)
    
    logs = get_kingdom_activity_logs(kingdom)
    
    # Пагинация
    paginator = Paginator(logs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'kingdom': kingdom,
    }
    
    return render(request, 'action_logs/kingdom_logs.html', context)


@staff_member_required
def logs_statistics(request):
    """Статистика логов для администраторов"""
    # Общая статистика
    total_logs = ActionLog.objects.count()
    
    # Статистика по дням (последние 30 дней)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    daily_stats = ActionLog.objects.filter(
        created_at__gte=thirty_days_ago
    ).extra(
        select={'day': 'date(created_at)'}
    ).values('day').annotate(
        count=Count('id')
    ).order_by('day')
    
    # Статистика по действиям
    action_stats = ActionLog.objects.values('action').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Статистика по ролям пользователей
    role_stats = ActionLog.objects.values('user__role').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Статистика по королевствам
    kingdom_stats = ActionLog.objects.filter(
        user__citizen_profile__isnull=False
    ).values('user__citizen_profile__kingdom__name').annotate(
        count=Count('id')
    ).order_by('-count')
    
    context = {
        'total_logs': total_logs,
        'daily_stats': daily_stats,
        'action_stats': action_stats,
        'role_stats': role_stats,
        'kingdom_stats': kingdom_stats,
    }
    
    return render(request, 'action_logs/logs_statistics.html', context)
