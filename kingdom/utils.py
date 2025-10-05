import logging
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from kingdom.models import ActionLog

User = get_user_model()
logger = logging.getLogger(__name__)


def log_user_action(user, action, description='', metadata=None, request=None):
    """
    Логирование действий пользователя
    
    Args:
        user: Пользователь, совершивший действие
        action: Тип действия (из ActionLog.ACTION_CHOICES)
        description: Описание действия
        metadata: Дополнительные метаданные (словарь)
        request: HTTP запрос (для получения IP и User-Agent)
    """
    try:
        ip_address = None
        user_agent = None
        
        if request:
            # Получаем IP адрес
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0].strip()
            else:
                ip_address = request.META.get('REMOTE_ADDR')
            
            # Получаем User-Agent
            user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Создаем запись в логе
        ActionLog.objects.create(
            user=user,
            action=action,
            description=description,
            metadata=metadata or {},
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Также логируем в файл
        logger.info(f'User action: {user.email} - {action} - {description}')
        
    except Exception as e:
        logger.error(f'Error logging user action: {str(e)}')


def log_test_start(user, test_attempt):
    """Логирование начала тестирования"""
    log_user_action(
        user=user,
        action='test_start',
        description=f'Начало тестирования "{test_attempt.test.title}"',
        metadata={
            'test_id': str(test_attempt.test.id),
            'attempt_id': str(test_attempt.id),
            'total_questions': test_attempt.total_questions
        }
    )


def log_test_complete(user, test_attempt):
    """Логирование завершения тестирования"""
    log_user_action(
        user=user,
        action='test_complete',
        description=f'Завершение тестирования "{test_attempt.test.title}". Результат: {test_attempt.score}/{test_attempt.total_questions}',
        metadata={
            'test_id': str(test_attempt.test.id),
            'attempt_id': str(test_attempt.id),
            'score': test_attempt.score,
            'total_questions': test_attempt.total_questions,
            'percentage': test_attempt.percentage
        }
    )


def log_enrollment(king_user, citizen):
    """Логирование зачисления подданного"""
    log_user_action(
        user=king_user,
        action='enrollment',
        description=f'Зачисление подданного {citizen.user.get_full_name()} в королевство {citizen.kingdom.name}',
        metadata={
            'citizen_id': str(citizen.id),
            'citizen_email': citizen.user.email,
            'kingdom_id': str(citizen.kingdom.id),
            'kingdom_name': citizen.kingdom.name
        }
    )


def log_login(user, request=None):
    """Логирование входа пользователя"""
    log_user_action(
        user=user,
        action='login',
        description=f'Вход пользователя {user.get_full_name()}',
        request=request
    )


def log_logout(user, request=None):
    """Логирование выхода пользователя"""
    log_user_action(
        user=user,
        action='logout',
        description=f'Выход пользователя {user.get_full_name()}',
        request=request
    )


def log_registration(user, request=None):
    """Логирование регистрации пользователя"""
    log_user_action(
        user=user,
        action='register',
        description=f'Регистрация пользователя {user.get_full_name()} с ролью {user.get_role_display()}',
        metadata={
            'role': user.role,
            'email': user.email
        },
        request=request
    )


def get_user_activity_logs(user, limit=50):
    """Получение логов активности пользователя"""
    return ActionLog.objects.filter(user=user).order_by('-created_at')[:limit]


def get_kingdom_activity_logs(kingdom, limit=100):
    """Получение логов активности по королевству"""
    return ActionLog.objects.filter(
        user__citizen_profile__kingdom=kingdom
    ).union(
        ActionLog.objects.filter(
            user__king_profile__kingdom=kingdom
        )
    ).order_by('-created_at')[:limit]


def export_logs_to_excel(logs, filename=None):
    """
    Экспорт логов в Excel файл
    
    Args:
        logs: QuerySet логов
        filename: Имя файла (опционально)
    
    Returns:
        HttpResponse с Excel файлом
    """
    try:
        import pandas as pd
        from django.http import HttpResponse
        
        # Преобразуем логи в DataFrame
        data = []
        for log in logs:
            data.append({
                'Дата': log.created_at.strftime('%d.%m.%Y %H:%M:%S'),
                'Пользователь': log.user.get_full_name(),
                'Email': log.user.email,
                'Роль': log.user.get_role_display(),
                'Действие': log.get_action_display(),
                'Описание': log.description,
                'IP адрес': log.ip_address or '',
                'User Agent': log.user_agent or '',
                'Метаданные': str(log.metadata) if log.metadata else ''
            })
        
        df = pd.DataFrame(data)
        
        # Создаем Excel файл в памяти
        output = pd.ExcelWriter(filename or 'logs.xlsx', engine='openpyxl')
        df.to_excel(output, index=False, sheet_name='Логи действий')
        
        # Настраиваем ширину колонок
        worksheet = output.sheets['Логи действий']
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
        
        output.close()
        
        # Читаем файл и возвращаем как HttpResponse
        with open(filename or 'logs.xlsx', 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="{filename or "logs.xlsx"}"'
            return response
            
    except ImportError:
        logger.error('pandas не установлен. Установите: pip install pandas openpyxl')
        return None
    except Exception as e:
        logger.error(f'Ошибка при экспорте логов: {str(e)}')
        return None
