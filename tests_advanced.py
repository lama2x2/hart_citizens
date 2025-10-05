"""
Расширенные тесты для моделей Hart Citizens
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

from kingdom.models import Kingdom, King, Citizen, Test, Question, TestAttempt, Answer
from action_logs.models import ActionLog

User = get_user_model()


class KingdomModelAdvancedTest(TestCase):
    """Расширенные тесты для модели Kingdom"""
    
    def setUp(self):
        self.kingdom = Kingdom.objects.create(
            name='Королевство Тестов',
            description='Описание тестового королевства'
        )
    
    def test_kingdom_creation_with_uuid(self):
        """Тест создания королевства с UUID"""
        self.assertIsNotNone(self.kingdom.id)
        # UUID объект, не строка
        self.assertIsNotNone(str(self.kingdom.id))
    
    def test_kingdom_timestamps(self):
        """Тест временных меток королевства"""
        self.assertIsNotNone(self.kingdom.created_at)
        self.assertIsNotNone(self.kingdom.updated_at)
        self.assertLessEqual(self.kingdom.created_at, timezone.now())
    
    def test_kingdom_str_representation(self):
        """Тест строкового представления"""
        self.assertEqual(str(self.kingdom), 'Королевство Тестов')
    
    def test_kingdom_relationships(self):
        """Тест связей королевства"""
        # Создаем короля для королевства
        king_user = User.objects.create_user(
            username='kinguser',
            first_name='Король',
            last_name='Тестов',
            role='king'
        )
        king = King.objects.create(
            user=king_user,
            kingdom=self.kingdom,
            max_citizens=5
        )
        
        # Проверяем связь (related_name='king', не 'kings')
        self.assertEqual(king.kingdom, self.kingdom)
        self.assertEqual(self.kingdom.king, king)


class KingModelAdvancedTest(TestCase):
    """Расширенные тесты для модели King"""
    
    def setUp(self):
        self.kingdom = Kingdom.objects.create(name='Тестовое Королевство')
        self.king_user = User.objects.create_user(
            username='kinguser',
            first_name='Король',
            last_name='Тестов',
            role='king'
        )
        self.king = King.objects.create(
            user=self.king_user,
            kingdom=self.kingdom,
            max_citizens=1  # Устанавливаем лимит в 1 для теста
        )
    
    def test_king_creation(self):
        """Тест создания короля"""
        self.assertEqual(self.king.user, self.king_user)
        self.assertEqual(self.king.kingdom, self.kingdom)
        self.assertEqual(self.king.max_citizens, 1)
        self.assertEqual(self.king.current_citizens_count, 0)
    
    def test_king_str_representation(self):
        """Тест строкового представления короля"""
        expected = f"{self.king_user.get_full_name()} - {self.kingdom.name}"
        self.assertEqual(str(self.king), expected)
    
    def test_king_can_enroll_citizen(self):
        """Тест возможности зачисления подданного"""
        # Создаем подданного
        citizen_user = User.objects.create_user(
            username='citizenuser',
            email='citizen@example.com',
            first_name='Подданный',
            last_name='Тестов',
            role='citizen'
        )
        citizen = Citizen.objects.create(
            user=citizen_user,
            kingdom=self.kingdom,
            age=25,
            pigeon_email='citizen@example.com'
        )
        
        # Проверяем, что король может зачислить подданного
        self.assertTrue(self.king.can_accept_more_citizens)
        
        # Зачисляем подданного
        citizen.enroll(self.king)
        
        # Проверяем, что подданный зачислен
        self.assertTrue(citizen.is_enrolled)
        self.assertEqual(citizen.king, self.king)
        self.assertIsNotNone(citizen.enrolled_at)
        
        # Проверяем, что король больше не может принимать подданных
        self.assertFalse(self.king.can_accept_more_citizens)
    
    def test_king_max_citizens_limit(self):
        """Тест лимита подданных короля"""
        # Устанавливаем лимит в 2
        self.king.max_citizens = 2
        self.king.save()
        
        # Создаем 2 подданных
        for i in range(2):
            citizen_user = User.objects.create_user(
                username=f'citizen{i}',
                email=f'citizen{i}@example.com',
                first_name=f'Подданный{i}',
                last_name='Тестов',
                role='citizen'
            )
            citizen = Citizen.objects.create(
                user=citizen_user,
                kingdom=self.kingdom,
                age=25,
                pigeon_email=f'citizen{i}@example.com'
            )
            citizen.enroll(self.king)
        
        # Проверяем, что больше нельзя зачислить
        self.assertFalse(self.king.can_accept_more_citizens)


class CitizenModelAdvancedTest(TestCase):
    """Расширенные тесты для модели Citizen"""
    
    def setUp(self):
        self.kingdom = Kingdom.objects.create(name='Тестовое Королевство')
        self.king_user = User.objects.create_user(
            username='kinguser',
            first_name='Король',
            last_name='Тестов',
            role='king'
        )
        self.king = King.objects.create(
            user=self.king_user,
            kingdom=self.kingdom,
            max_citizens=5
        )
        self.citizen_user = User.objects.create_user(
            username='citizenuser',
            email='citizen@example.com',
            first_name='Подданный',
            last_name='Тестов',
            role='citizen'
        )
        self.citizen = Citizen.objects.create(
            user=self.citizen_user,
            kingdom=self.kingdom,
            age=25,
            pigeon_email='citizen@example.com'
        )
    
    def test_citizen_creation(self):
        """Тест создания подданного"""
        self.assertEqual(self.citizen.user, self.citizen_user)
        self.assertEqual(self.citizen.kingdom, self.kingdom)
        self.assertEqual(self.citizen.age, 25)
        self.assertEqual(self.citizen.pigeon_email, 'citizen@example.com')
        self.assertFalse(self.citizen.is_enrolled)
        self.assertIsNone(self.citizen.king)
    
    def test_citizen_str_representation(self):
        """Тест строкового представления подданного"""
        expected = f"{self.citizen_user.get_full_name()} ({self.kingdom.name})"
        self.assertEqual(str(self.citizen), expected)
    
    def test_citizen_enrollment(self):
        """Тест зачисления подданного"""
        # Зачисляем подданного
        self.citizen.enroll(self.king)
        
        self.assertTrue(self.citizen.is_enrolled)
        self.assertEqual(self.citizen.king, self.king)
        self.assertIsNotNone(self.citizen.enrolled_at)
    
    def test_citizen_email_required(self):
        """Тест обязательности email для подданных"""
        # Создаем подданного без email
        citizen_user_no_email = User.objects.create_user(
            username='citizennoemail',
            email='citizen@example.com',  # Добавляем email для создания пользователя
            first_name='Подданный',
            last_name='БезEmail',
            role='citizen'
        )
        
        # Это должно вызвать ошибку валидации при создании Citizen без pigeon_email
        with self.assertRaises(ValidationError):
            citizen = Citizen(
                user=citizen_user_no_email,
                kingdom=self.kingdom,
                age=25
                # Не указываем pigeon_email
            )
            citizen.full_clean()


class TestModelAdvancedTest(TestCase):
    """Расширенные тесты для модели Test"""
    
    def setUp(self):
        self.kingdom = Kingdom.objects.create(name='Тестовое Королевство')
        self.test = Test.objects.create(
            kingdom=self.kingdom,
            title='Тестовое испытание',
            description='Описание тестового испытания',
            is_active=True
        )
    
    def test_test_creation(self):
        """Тест создания теста"""
        self.assertEqual(self.test.kingdom, self.kingdom)
        self.assertEqual(self.test.title, 'Тестовое испытание')
        self.assertTrue(self.test.is_active)
        self.assertIsNotNone(self.test.created_at)
    
    def test_test_str_representation(self):
        """Тест строкового представления теста"""
        expected = f"{self.test.title} ({self.kingdom.name})"
        self.assertEqual(str(self.test), expected)
    
    def test_test_questions_relationship(self):
        """Тест связи теста с вопросами"""
        # Создаем вопросы
        question1 = Question.objects.create(
            test=self.test,
            text='Первый вопрос?',
            correct_answer=True,
            order=1
        )
        question2 = Question.objects.create(
            test=self.test,
            text='Второй вопрос?',
            correct_answer=False,
            order=2
        )
        
        # Проверяем связь
        questions = self.test.questions.all()
        self.assertEqual(questions.count(), 2)
        self.assertIn(question1, questions)
        self.assertIn(question2, questions)


class QuestionModelAdvancedTest(TestCase):
    """Расширенные тесты для модели Question"""
    
    def setUp(self):
        self.kingdom = Kingdom.objects.create(name='Тестовое Королевство')
        self.test = Test.objects.create(
            kingdom=self.kingdom,
            title='Тестовое испытание'
        )
        self.question = Question.objects.create(
            test=self.test,
            text='Это тестовый вопрос?',
            correct_answer=True,
            order=1
        )
    
    def test_question_creation(self):
        """Тест создания вопроса"""
        self.assertEqual(self.question.test, self.test)
        self.assertEqual(self.question.text, 'Это тестовый вопрос?')
        self.assertTrue(self.question.correct_answer)
        self.assertEqual(self.question.order, 1)
    
    def test_question_str_representation(self):
        """Тест строкового представления вопроса"""
        expected = 'Это тестовый вопрос?...'
        self.assertEqual(str(self.question), expected)
    
    def test_question_ordering(self):
        """Тест упорядочивания вопросов"""
        # Создаем еще вопросы
        question2 = Question.objects.create(
            test=self.test,
            text='Второй вопрос?',
            correct_answer=False,
            order=2
        )
        question3 = Question.objects.create(
            test=self.test,
            text='Третий вопрос?',
            correct_answer=True,
            order=3
        )
        
        # Проверяем порядок
        questions = self.test.questions.all().order_by('order')
        self.assertEqual(questions[0], self.question)
        self.assertEqual(questions[1], question2)
        self.assertEqual(questions[2], question3)


class TestAttemptModelAdvancedTest(TestCase):
    """Расширенные тесты для модели TestAttempt"""
    
    def setUp(self):
        self.kingdom = Kingdom.objects.create(name='Тестовое Королевство')
        self.citizen_user = User.objects.create_user(
            username='citizenuser',
            email='citizen@example.com',
            first_name='Подданный',
            last_name='Тестов',
            role='citizen'
        )
        self.citizen = Citizen.objects.create(
            user=self.citizen_user,
            kingdom=self.kingdom,
            age=25,
            pigeon_email='citizen@example.com'
        )
        self.test = Test.objects.create(
            kingdom=self.kingdom,
            title='Тестовое испытание'
        )
        self.attempt = TestAttempt.objects.create(
            citizen=self.citizen,
            test=self.test,
            total_questions=5,
            score=3  # правильные ответы
        )
    
    def test_attempt_creation(self):
        """Тест создания попытки"""
        self.assertEqual(self.attempt.citizen, self.citizen)
        self.assertEqual(self.attempt.test, self.test)
        self.assertEqual(self.attempt.total_questions, 5)
        self.assertEqual(self.attempt.score, 3)
        self.assertEqual(self.attempt.status, 'in_progress')
        self.assertIsNone(self.attempt.completed_at)
    
    def test_attempt_percentage_calculation(self):
        """Тест расчета процента правильных ответов"""
        percentage = self.attempt.percentage
        expected = (3 / 5) * 100
        self.assertEqual(percentage, expected)
    
    def test_attempt_completion(self):
        """Тест завершения попытки"""
        self.attempt.status = 'completed'
        self.attempt.completed_at = timezone.now()
        self.attempt.save()
        
        self.assertEqual(self.attempt.status, 'completed')
        self.assertIsNotNone(self.attempt.completed_at)
    
    def test_attempt_str_representation(self):
        """Тест строкового представления попытки"""
        expected = f"{self.citizen_user.get_full_name()} - {self.test.title}"
        self.assertEqual(str(self.attempt), expected)


class AnswerModelAdvancedTest(TestCase):
    """Расширенные тесты для модели Answer"""
    
    def setUp(self):
        self.kingdom = Kingdom.objects.create(name='Тестовое Королевство')
        self.citizen_user = User.objects.create_user(
            username='citizenuser',
            email='citizen@example.com',
            first_name='Подданный',
            last_name='Тестов',
            role='citizen'
        )
        self.citizen = Citizen.objects.create(
            user=self.citizen_user,
            kingdom=self.kingdom,
            age=25,
            pigeon_email='citizen@example.com'
        )
        self.test = Test.objects.create(
            kingdom=self.kingdom,
            title='Тестовое испытание'
        )
        self.question = Question.objects.create(
            test=self.test,
            text='Это тестовый вопрос?',
            correct_answer=True,
            order=1
        )
        self.attempt = TestAttempt.objects.create(
            citizen=self.citizen,
            test=self.test,
            total_questions=1
        )
        self.answer = Answer.objects.create(
            attempt=self.attempt,
            question=self.question,
            answer=True
            # is_correct будет заполнено автоматически
        )
    
    def test_answer_creation(self):
        """Тест создания ответа"""
        self.assertEqual(self.answer.attempt, self.attempt)
        self.assertEqual(self.answer.question, self.question)
        self.assertTrue(self.answer.answer)
        self.assertTrue(self.answer.is_correct)  # answer=True, correct_answer=True
    
    def test_answer_correctness(self):
        """Тест правильности ответа"""
        # Правильный ответ (уже создан в setUp)
        self.assertTrue(self.answer.is_correct)
        
        # Создаем новый вопрос для неправильного ответа
        question2 = Question.objects.create(
            test=self.test,
            text='Второй вопрос?',
            correct_answer=False,
            order=2
        )
        
        # Неправильный ответ
        wrong_answer = Answer.objects.create(
            attempt=self.attempt,
            question=question2,
            answer=True  # Ответ True, но правильный ответ False
        )
        self.assertFalse(wrong_answer.is_correct)
    
    def test_answer_str_representation(self):
        """Тест строкового представления ответа"""
        expected = f"{self.citizen_user.get_full_name()} - {self.question.text[:20]}..."
        self.assertEqual(str(self.answer), expected)


class ActionLogModelAdvancedTest(TestCase):
    """Расширенные тесты для модели ActionLog"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            first_name='Тест',
            last_name='Пользователь',
            role='citizen'
        )
        self.action_log = ActionLog.objects.create(
            user=self.user,
            action='login',
            description='Тестовый вход в систему',
            ip_address='127.0.0.1',
            user_agent='Test Browser',
            metadata={'test': 'data'}
        )
    
    def test_action_log_creation(self):
        """Тест создания лога действия"""
        self.assertEqual(self.action_log.user, self.user)
        self.assertEqual(self.action_log.action, 'login')
        self.assertEqual(self.action_log.description, 'Тестовый вход в систему')
        self.assertEqual(self.action_log.ip_address, '127.0.0.1')
        self.assertEqual(self.action_log.user_agent, 'Test Browser')
        self.assertEqual(self.action_log.metadata, {'test': 'data'})
        self.assertIsNotNone(self.action_log.created_at)
    
    def test_action_log_str_representation(self):
        """Тест строкового представления лога"""
        expected = f"{self.user.get_full_name()} - {self.action_log.get_action_display()} ({self.action_log.created_at.strftime('%d.%m.%Y %H:%M')})"
        self.assertEqual(str(self.action_log), expected)
    
    def test_action_log_get_action_display(self):
        """Тест получения отображаемого названия действия"""
        display = self.action_log.get_action_display()
        self.assertEqual(display, 'Вход в систему')
    
    def test_action_log_choices(self):
        """Тест доступных вариантов действий"""
        choices = ActionLog.ACTION_CHOICES
        self.assertIn(('login', 'Вход в систему'), choices)
        self.assertIn(('logout', 'Выход из системы'), choices)
        self.assertIn(('register', 'Регистрация'), choices)
        self.assertIn(('test_start', 'Начало тестирования'), choices)
        self.assertIn(('test_complete', 'Завершение тестирования'), choices)
        self.assertIn(('enrollment', 'Зачисление подданного'), choices)
