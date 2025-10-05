from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
import logging
import json

from .models import (
    Kingdom, King, Citizen, Test, Question, 
    TestAttempt, Answer
)
from action_logs.models import ActionLog
from .forms import CitizenProfileForm, TestAnswerForm, TestAttemptForm
from users.models import User

logger = logging.getLogger('kingdom')


@method_decorator(login_required, name='dispatch')
class KingDashboardView(TemplateView):
    """Панель управления короля"""
    template_name = 'kingdom/king_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        try:
            king = user.king_profile
            context['king'] = king
            
            # Получаем подданных, прошедших тест, но не зачисленных
            passed_citizens = Citizen.objects.filter(
                kingdom=king.kingdom,
                is_enrolled=False
            ).select_related('user')
            
            # Фильтруем только тех, кто прошел тест
            enrolled_citizens = []
            for citizen in passed_citizens:
                if citizen.test_attempts.filter(status='completed').exists():
                    enrolled_citizens.append(citizen)
            
            context['enrolled_citizens'] = enrolled_citizens
            context['current_citizens'] = king.citizens.all()
            context['can_accept_more'] = king.can_accept_more_citizens
            
        except King.DoesNotExist:
            messages.error(self.request, 'Профиль короля не найден.')
        
        return context


@method_decorator(login_required, name='dispatch')
class CitizenDashboardView(TemplateView):
    """Панель управления подданного"""
    template_name = 'kingdom/citizen_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        try:
            citizen = user.citizen_profile
            context['citizen'] = citizen
            
            # Проверяем статус зачисления
            if citizen.is_enrolled and citizen.king:
                context['king'] = citizen.king
                context['enrolled_at'] = citizen.enrolled_at
            
            # Получаем тестовое испытание
            try:
                test = citizen.kingdom.test
                context['test'] = test
                
                # Проверяем, проходил ли уже тест
                last_attempt = citizen.test_attempts.filter(test=test).order_by('-started_at').first()
                if last_attempt:
                    context['last_attempt'] = last_attempt
                    context['has_passed_test'] = last_attempt.status == 'completed'
                else:
                    context['has_passed_test'] = False
                
            except Test.DoesNotExist:
                context['test'] = None
                context['has_passed_test'] = False
            
        except Citizen.DoesNotExist:
            messages.error(self.request, 'Профиль подданного не найден.')
        
        return context


@method_decorator(login_required, name='dispatch')
class TestView(TemplateView):
    """Страница прохождения теста"""
    template_name = 'kingdom/test.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        try:
            citizen = user.citizen_profile
            test = citizen.kingdom.test
            
            # Проверяем, есть ли активная попытка
            active_attempt = citizen.test_attempts.filter(
                test=test,
                status='in_progress'
            ).first()
            
            if active_attempt:
                context['attempt'] = active_attempt
                # Получаем вопросы, на которые еще не отвечали
                answered_questions = active_attempt.answers.values_list('question_id', flat=True)
                remaining_questions = test.questions.exclude(id__in=answered_questions).order_by('order')
                context['remaining_questions'] = remaining_questions
                context['current_question'] = remaining_questions.first()
            else:
                # Создаем новую попытку
                attempt = TestAttempt.objects.create(
                    citizen=citizen,
                    test=test,
                    total_questions=test.questions.count()
                )
                context['attempt'] = attempt
                context['current_question'] = test.questions.order_by('order').first()
            
        except (Citizen.DoesNotExist, Test.DoesNotExist) as e:
            messages.error(self.request, 'Тестовое испытание не найдено.')
            return redirect('kingdom:citizen_dashboard')
        
        return context


@login_required
def start_test(request):
    """Начало тестирования"""
    try:
        citizen = request.user.citizen_profile
        test = citizen.kingdom.test
        
        # Проверяем, есть ли уже активная попытка
        active_attempt = citizen.test_attempts.filter(
            test=test,
            status='in_progress'
        ).first()
        
        if active_attempt:
            return redirect('kingdom:test')
        
        # Создаем новую попытку
        attempt = TestAttempt.objects.create(
            citizen=citizen,
            test=test,
            total_questions=test.questions.count()
        )
        
        # Логируем начало тестирования
        ActionLog.objects.create(
            user=request.user,
            action='test_start',
            description=f'Начало тестирования для {citizen.user.get_full_name()}',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        logger.info(f'Подданный {citizen.user.email} начал тестирование')
        
        return redirect('kingdom:test')
    
    except (Citizen.DoesNotExist, Test.DoesNotExist):
        messages.error(request, 'Тестовое испытание не найдено.')
        return redirect('kingdom:citizen_dashboard')


@login_required
def answer_question(request, question_id):
    """Ответ на вопрос"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не разрешен'}, status=405)
    
    try:
        citizen = request.user.citizen_profile
        question = get_object_or_404(Question, id=question_id)
        
        # Проверяем, что вопрос принадлежит тесту королевства подданного
        if question.test.kingdom != citizen.kingdom:
            return JsonResponse({'error': 'Вопрос не принадлежит вашему королевству'}, status=400)
        
        # Получаем активную попытку
        attempt = citizen.test_attempts.filter(
            test=question.test,
            status='in_progress'
        ).first()
        
        if not attempt:
            return JsonResponse({'error': 'Активная попытка не найдена'}, status=400)
        
        # Получаем ответ
        answer_value = request.POST.get('answer')
        if answer_value is None:
            return JsonResponse({'error': 'Ответ не предоставлен'}, status=400)
        
        answer_value = answer_value.lower() == 'true'
        
        # Сохраняем ответ
        answer, created = Answer.objects.get_or_create(
            attempt=attempt,
            question=question,
            defaults={
                'answer': answer_value,
                'is_correct': answer_value == question.correct_answer,
            }
        )
        
        if not created:
            answer.answer = answer_value
            answer.is_correct = answer_value == question.correct_answer
            answer.save()
        
        # Обновляем счетчик правильных ответов
        correct_answers = attempt.answers.filter(is_correct=True).count()
        attempt.score = correct_answers
        attempt.save()
        
        # Проверяем, завершен ли тест
        total_answered = attempt.answers.count()
        if total_answered >= attempt.total_questions:
            attempt.status = 'completed'
            attempt.completed_at = timezone.now()
            attempt.save()
            
            # Логируем завершение тестирования
            ActionLog.objects.create(
                user=request.user,
                action='test_complete',
                description=f'Завершение тестирования для {citizen.user.get_full_name()}. Результат: {attempt.score}/{attempt.total_questions}',
                metadata={'score': attempt.score, 'total': attempt.total_questions},
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            logger.info(f'Подданный {citizen.user.email} завершил тестирование с результатом {attempt.score}/{attempt.total_questions}')
        
        return JsonResponse({
            'success': True,
            'is_correct': answer.is_correct,
            'completed': attempt.status == 'completed',
            'score': attempt.score,
            'total': attempt.total_questions
        })
    
    except Exception as e:
        logger.error(f'Ошибка при ответе на вопрос: {str(e)}')
        return JsonResponse({'error': 'Внутренняя ошибка сервера'}, status=500)


@login_required
def enroll_citizen(request, citizen_id):
    """Зачисление подданного королем"""
    if not request.user.is_king:
        messages.error(request, 'Только короли могут зачислять подданных.')
        return redirect('kingdom:king_dashboard')
    
    try:
        king = request.user.king_profile
        citizen = get_object_or_404(Citizen, id=citizen_id)
        
        # Проверяем, что подданный принадлежит королевству короля
        if citizen.kingdom != king.kingdom:
            messages.error(request, 'Подданный не принадлежит вашему королевству.')
            return redirect('kingdom:king_dashboard')
        
        # Проверяем, что подданный прошел тест
        if not citizen.test_attempts.filter(status='completed').exists():
            messages.error(request, 'Подданный не прошел тестовое испытание.')
            return redirect('kingdom:king_dashboard')
        
        # Проверяем лимит подданных
        if not king.can_accept_more_citizens:
            messages.error(request, f'Вы не можете принять больше {king.max_citizens} подданных.')
            return redirect('kingdom:king_dashboard')
        
        # Зачисляем подданного
        citizen.enroll(king)
        
        # Логируем зачисление
        ActionLog.objects.create(
            user=request.user,
            action='enrollment',
            description=f'Зачисление подданного {citizen.user.get_full_name()} королем {king.user.get_full_name()}',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        logger.info(f'Король {king.user.email} зачислил подданного {citizen.user.email}')
        
        messages.success(request, f'Подданный {citizen.user.get_full_name()} успешно зачислен!')
        
    except Exception as e:
        logger.error(f'Ошибка при зачислении подданного: {str(e)}')
        messages.error(request, 'Ошибка при зачислении подданного.')
    
    return redirect('kingdom:king_dashboard')


@method_decorator(login_required, name='dispatch')
class CitizenTestResultsView(DetailView):
    """Результаты тестирования подданного"""
    model = TestAttempt
    template_name = 'kingdom/citizen_test_results.html'
    context_object_name = 'attempt'
    
    def get_queryset(self):
        """Фильтруем попытки только для текущего пользователя"""
        return TestAttempt.objects.filter(citizen__user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['answers'] = self.object.answers.select_related('question').order_by('question__order')
        return context


@method_decorator(login_required, name='dispatch')
class KingCitizenDetailsView(DetailView):
    """Детали подданного для короля"""
    model = Citizen
    template_name = 'kingdom/king_citizen_details.html'
    context_object_name = 'citizen'
    
    def get_queryset(self):
        """Фильтруем подданных только из королевства короля"""
        if self.request.user.is_king:
            return Citizen.objects.filter(kingdom=self.request.user.king_profile.kingdom)
        return Citizen.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        citizen = self.object
        
        # Получаем последнюю попытку тестирования
        last_attempt = citizen.test_attempts.filter(status='completed').order_by('-completed_at').first()
        if last_attempt:
            context['last_attempt'] = last_attempt
            context['answers'] = last_attempt.answers.select_related('question').order_by('question__order')
        
        return context


def get_client_ip(request):
    """Получение IP адреса клиента"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip