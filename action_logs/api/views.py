from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta

from ..models import ActionLog
from ..utils import export_logs_to_excel
from .serializers import ActionLogSerializer


class ActionLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для логов действий"""
    
    queryset = ActionLog.objects.all()
    serializer_class = ActionLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['action', 'user__role']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'description']
    ordering_fields = ['created_at', 'action']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Фильтрация queryset в зависимости от роли пользователя"""
        user = self.request.user
        
        if user.is_staff:
            # Администраторы видят все логи
            return ActionLog.objects.all().select_related('user')
        elif user.is_king:
            # Короли видят логи своего королевства
            kingdom = user.king_profile.kingdom
            return ActionLog.objects.filter(
                Q(user__citizen_profile__kingdom=kingdom) |
                Q(user__king_profile__kingdom=kingdom)
            ).select_related('user')
        elif user.is_citizen:
            # Подданные видят только свои логи
            return ActionLog.objects.filter(user=user).select_related('user')
        else:
            # Обычные пользователи видят только свои логи
            return ActionLog.objects.filter(user=user).select_related('user')
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def user_logs(self, request):
        """Логи текущего пользователя"""
        logs = ActionLog.objects.filter(user=request.user).order_by('-created_at')
        
        # Пагинация
        page = self.paginate_queryset(logs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def kingdom_logs(self, request):
        """Логи королевства пользователя"""
        user = request.user
        
        if user.is_king:
            kingdom = user.king_profile.kingdom
        elif user.is_citizen:
            kingdom = user.citizen_profile.kingdom
        else:
            return Response(
                {'error': 'Недостаточно прав для просмотра логов королевства'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        logs = ActionLog.objects.filter(
            Q(user__citizen_profile__kingdom=kingdom) |
            Q(user__king_profile__kingdom=kingdom)
        ).order_by('-created_at')
        
        # Пагинация
        page = self.paginate_queryset(logs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAdminUser])
    def export(self, request):
        """Экспорт логов в Excel"""
        try:
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
                return Response(
                    {'error': 'Ошибка при экспорте логов'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        except Exception as e:
            return Response(
                {'error': 'Внутренняя ошибка сервера'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAdminUser])
    def statistics(self, request):
        """Статистика логов для администраторов"""
        from django.db.models import Count
        
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
        
        return Response({
            'total_logs': total_logs,
            'daily_stats': list(daily_stats),
            'action_stats': list(action_stats),
            'role_stats': list(role_stats),
            'kingdom_stats': list(kingdom_stats),
        })
