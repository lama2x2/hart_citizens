from rest_framework import serializers, status, viewsets, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q
import logging

from kingdom.models import (
    Kingdom, King, Citizen, Test, Question, 
    TestAttempt, Answer, ActionLog
)
from users.models import User

logger = logging.getLogger('kingdom')


class KingdomSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Kingdom"""
    
    class Meta:
        model = Kingdom
        fields = ('id', 'name', 'description', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class KingSerializer(serializers.ModelSerializer):
    """Сериализатор для модели King"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    kingdom_name = serializers.CharField(source='kingdom.name', read_only=True)
    current_citizens_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = King
        fields = ('id', 'user_name', 'kingdom_name', 'max_citizens', 'current_citizens_count', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at', 'current_citizens_count')


class CitizenSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Citizen"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    kingdom_name = serializers.CharField(source='kingdom.name', read_only=True)
    king_name = serializers.CharField(source='king.user.get_full_name', read_only=True)
    
    class Meta:
        model = Citizen
        fields = ('id', 'user_name', 'kingdom_name', 'age', 'pigeon_email', 'is_enrolled', 'king_name', 'enrolled_at', 'created_at', 'updated_at')
        read_only_fields = ('id', 'is_enrolled', 'king_name', 'enrolled_at', 'created_at', 'updated_at')


class QuestionSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Question"""
    
    class Meta:
        model = Question
        fields = ('id', 'text', 'order', 'created_at')
        read_only_fields = ('id', 'created_at')


class TestSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Test"""
    kingdom_name = serializers.CharField(source='kingdom.name', read_only=True)
    questions = QuestionSerializer(many=True, read_only=True)
    questions_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Test
        fields = ('id', 'title', 'description', 'kingdom_name', 'is_active', 'questions', 'questions_count', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at', 'questions_count')


class AnswerSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Answer"""
    question_text = serializers.CharField(source='question.text', read_only=True)
    
    class Meta:
        model = Answer
        fields = ('id', 'question_text', 'answer', 'is_correct', 'answered_at')
        read_only_fields = ('id', 'question_text', 'is_correct', 'answered_at')


class TestAttemptSerializer(serializers.ModelSerializer):
    """Сериализатор для модели TestAttempt"""
    citizen_name = serializers.CharField(source='citizen.user.get_full_name', read_only=True)
    test_title = serializers.CharField(source='test.title', read_only=True)
    answers = AnswerSerializer(many=True, read_only=True)
    percentage = serializers.FloatField(read_only=True)
    
    class Meta:
        model = TestAttempt
        fields = ('id', 'citizen_name', 'test_title', 'status', 'score', 'total_questions', 'percentage', 'started_at', 'completed_at', 'answers')
        read_only_fields = ('id', 'citizen_name', 'test_title', 'score', 'total_questions', 'percentage', 'started_at', 'completed_at')


class ActionLogSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ActionLog"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    
    class Meta:
        model = ActionLog
        fields = ('id', 'user_name', 'action', 'action_display', 'description', 'metadata', 'ip_address', 'created_at')
        read_only_fields = ('id', 'user_name', 'action_display', 'created_at')


class KingdomViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для модели Kingdom"""
    queryset = Kingdom.objects.all()
    serializer_class = KingdomSerializer
    permission_classes = [IsAuthenticated]


class KingViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для модели King"""
    serializer_class = KingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Фильтруем королей по текущему пользователю"""
        if self.request.user.is_king:
            return King.objects.filter(user=self.request.user)
        return King.objects.none()


class CitizenViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Citizen"""
    serializer_class = CitizenSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Фильтруем подданных по текущему пользователю"""
        if self.request.user.is_citizen:
            return Citizen.objects.filter(user=self.request.user)
        elif self.request.user.is_king:
            return Citizen.objects.filter(kingdom=self.request.user.king_profile.kingdom)
        return Citizen.objects.none()
    
    def perform_update(self, serializer):
        """Обновление профиля подданного"""
        if self.request.user.is_citizen:
            serializer.save(user=self.request.user)
        else:
            serializer.save()


class TestViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для модели Test"""
    serializer_class = TestSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Фильтруем тесты по королевству пользователя"""
        if self.request.user.is_citizen:
            return Test.objects.filter(kingdom=self.request.user.citizen_profile.kingdom)
        elif self.request.user.is_king:
            return Test.objects.filter(kingdom=self.request.user.king_profile.kingdom)
        return Test.objects.none()


class TestAttemptViewSet(viewsets.ModelViewSet):
    """ViewSet для модели TestAttempt"""
    serializer_class = TestAttemptSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Фильтруем попытки по текущему пользователю"""
        if self.request.user.is_citizen:
            return TestAttempt.objects.filter(citizen__user=self.request.user)
        elif self.request.user.is_king:
            return TestAttempt.objects.filter(citizen__kingdom=self.request.user.king_profile.kingdom)
        return TestAttempt.objects.none()
    
    @action(detail=False, methods=['post'])
    def start_test(self, request):
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
                return Response({
                    'message': 'У вас уже есть активная попытка тестирования',
                    'attempt': TestAttemptSerializer(active_attempt).data
                })
            
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
                description=f'API начало тестирования для {citizen.user.get_full_name()}',
                ip_address=request.META.get('REMOTE_ADDR', ''),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            logger.info(f'API начало тестирования для подданного {citizen.user.email}')
            
            return Response({
                'message': 'Тестирование начато',
                'attempt': TestAttemptSerializer(attempt).data
            }, status=status.HTTP_201_CREATED)
        
        except (Citizen.DoesNotExist, Test.DoesNotExist):
            return Response({'error': 'Тестовое испытание не найдено'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def answer_question(self, request, pk=None):
        """Ответ на вопрос"""
        try:
            attempt = self.get_object()
            question_id = request.data.get('question_id')
            answer_value = request.data.get('answer')
            
            if not question_id or answer_value is None:
                return Response({'error': 'question_id и answer обязательны'}, status=status.HTTP_400_BAD_REQUEST)
            
            question = get_object_or_404(Question, id=question_id)
            
            # Проверяем, что вопрос принадлежит тесту попытки
            if question.test != attempt.test:
                return Response({'error': 'Вопрос не принадлежит данному тесту'}, status=status.HTTP_400_BAD_REQUEST)
            
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
                    description=f'API завершение тестирования для {attempt.citizen.user.get_full_name()}. Результат: {attempt.score}/{attempt.total_questions}',
                    metadata={'score': attempt.score, 'total': attempt.total_questions},
                    ip_address=request.META.get('REMOTE_ADDR', ''),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                logger.info(f'API завершение тестирования для подданного {attempt.citizen.user.email} с результатом {attempt.score}/{attempt.total_questions}')
            
            return Response({
                'is_correct': answer.is_correct,
                'completed': attempt.status == 'completed',
                'score': attempt.score,
                'total': attempt.total_questions
            })
        
        except Exception as e:
            logger.error(f'Ошибка при ответе на вопрос: {str(e)}')
            return Response({'error': 'Внутренняя ошибка сервера'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enroll_citizen(request, citizen_id):
    """API зачисления подданного королем"""
    if not request.user.is_king:
        return Response({'error': 'Только короли могут зачислять подданных'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        king = request.user.king_profile
        citizen = get_object_or_404(Citizen, id=citizen_id)
        
        # Проверяем, что подданный принадлежит королевству короля
        if citizen.kingdom != king.kingdom:
            return Response({'error': 'Подданный не принадлежит вашему королевству'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Проверяем, что подданный прошел тест
        if not citizen.test_attempts.filter(status='completed').exists():
            return Response({'error': 'Подданный не прошел тестовое испытание'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Проверяем лимит подданных
        if not king.can_accept_more_citizens:
            return Response({'error': f'Вы не можете принять больше {king.max_citizens} подданных'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Зачисляем подданного
        citizen.enroll(king)
        
        # Логируем зачисление
        ActionLog.objects.create(
            user=request.user,
            action='enrollment',
            description=f'API зачисление подданного {citizen.user.get_full_name()} королем {king.user.get_full_name()}',
            ip_address=request.META.get('REMOTE_ADDR', ''),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        logger.info(f'API зачисление подданного {citizen.user.email} королем {king.user.email}')
        
        return Response({
            'message': f'Подданный {citizen.user.get_full_name()} успешно зачислен!',
            'citizen': CitizenSerializer(citizen).data
        })
    
    except Exception as e:
        logger.error(f'Ошибка при зачислении подданного: {str(e)}')
        return Response({'error': 'Ошибка при зачислении подданного'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_data(request):
    """API получения данных для панели управления"""
    user = request.user
    
    if user.is_king:
        try:
            king = user.king_profile
            # Получаем подданных, прошедших тест, но не зачисленных
            passed_citizens = Citizen.objects.filter(
                kingdom=king.kingdom,
                is_enrolled=False
            ).select_related('user')
            
            enrolled_citizens = []
            for citizen in passed_citizens:
                if citizen.test_attempts.filter(status='completed').exists():
                    enrolled_citizens.append(citizen)
            
            return Response({
                'user_type': 'king',
                'king': KingSerializer(king).data,
                'enrolled_citizens': CitizenSerializer(enrolled_citizens, many=True).data,
                'current_citizens': CitizenSerializer(king.citizens.all(), many=True).data,
                'can_accept_more': king.can_accept_more_citizens
            })
        except King.DoesNotExist:
            return Response({'error': 'Профиль короля не найден'}, status=status.HTTP_404_NOT_FOUND)
    
    elif user.is_citizen:
        try:
            citizen = user.citizen_profile
            
            # Проверяем статус зачисления
            king_data = None
            if citizen.is_enrolled and citizen.king:
                king_data = KingSerializer(citizen.king).data
            
            # Получаем тестовое испытание
            test_data = None
            has_passed_test = False
            try:
                test = citizen.kingdom.test
                test_data = TestSerializer(test).data
                
                # Проверяем, проходил ли уже тест
                last_attempt = citizen.test_attempts.filter(test=test).order_by('-started_at').first()
                if last_attempt:
                    has_passed_test = last_attempt.status == 'completed'
                
            except Test.DoesNotExist:
                pass
            
            return Response({
                'user_type': 'citizen',
                'citizen': CitizenSerializer(citizen).data,
                'king': king_data,
                'test': test_data,
                'has_passed_test': has_passed_test
            })
        except Citizen.DoesNotExist:
            return Response({'error': 'Профиль подданного не найден'}, status=status.HTTP_404_NOT_FOUND)
    
    return Response({'error': 'Неизвестный тип пользователя'}, status=status.HTTP_400_BAD_REQUEST)
