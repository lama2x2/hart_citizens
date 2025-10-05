from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from celery import shared_task
import logging

logger = logging.getLogger('kingdom')


@shared_task
def send_enrollment_notification(citizen_email, king_name, kingdom_name):
    """
    Отправка уведомления подданному о зачислении
    """
    try:
        subject = f'Поздравляем! Вы зачислены в королевство {kingdom_name}'
        
        html_message = f"""
        <html>
        <body>
            <h2>Поздравляем!</h2>
            <p>Дорогой подданный,</p>
            <p>Мы рады сообщить, что король <strong>{king_name}</strong> 
            зачислил вас в подданные королевства <strong>{kingdom_name}</strong>!</p>
            <p>Теперь вы официально являетесь подданным этого королевства.</p>
            <p>С уважением,<br>
            Кадровая служба королевства</p>
        </body>
        </html>
        """
        
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[citizen_email],
            fail_silently=False,
        )
        
        logger.info(f'Уведомление о зачислении отправлено на {citizen_email}')
        
    except Exception as e:
        logger.error(f'Ошибка при отправке уведомления: {str(e)}')
        raise


@shared_task
def send_test_completion_notification(citizen_email, test_title, score, total_questions):
    """
    Отправка уведомления о завершении тестирования
    """
    try:
        percentage = round((score / total_questions) * 100, 2)
        
        subject = f'Результаты тестирования: {test_title}'
        
        html_message = f"""
        <html>
        <body>
            <h2>Результаты тестирования</h2>
            <p>Дорогой подданный,</p>
            <p>Вы завершили тестовое испытание <strong>"{test_title}"</strong>.</p>
            <p><strong>Ваш результат:</strong> {score} из {total_questions} ({percentage}%)</p>
            <p>Теперь король может рассмотреть вашу кандидатуру для зачисления в подданные.</p>
            <p>С уважением,<br>
            Кадровая служба королевства</p>
        </body>
        </html>
        """
        
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[citizen_email],
            fail_silently=False,
        )
        
        logger.info(f'Уведомление о завершении теста отправлено на {citizen_email}')
        
    except Exception as e:
        logger.error(f'Ошибка при отправке уведомления о тесте: {str(e)}')
        raise
