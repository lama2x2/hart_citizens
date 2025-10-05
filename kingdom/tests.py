from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from kingdom.models import Kingdom, King, Citizen, Test, Question, TestAttempt, Answer

User = get_user_model()


class UserModelTest(TestCase):
    """Тесты для модели User"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role='citizen'
        )
    
    def test_user_creation(self):
        """Тест создания пользователя"""
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.first_name, 'Test')
        self.assertEqual(self.user.last_name, 'User')
        self.assertEqual(self.user.role, 'citizen')
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_staff)
    
    def test_user_str(self):
        """Тест строкового представления пользователя"""
        expected = f"{self.user.first_name} {self.user.last_name} ({self.user.email})"
        self.assertEqual(str(self.user), expected)
    
    def test_user_is_citizen(self):
        """Тест проверки роли подданного"""
        self.assertTrue(self.user.is_citizen)
        self.assertFalse(self.user.is_king)


class KingdomModelTest(TestCase):
    """Тесты для модели Kingdom"""
    
    def setUp(self):
        self.kingdom = Kingdom.objects.create(
            name='Test Kingdom',
            description='Test Description'
        )
    
    def test_kingdom_creation(self):
        """Тест создания королевства"""
        self.assertEqual(self.kingdom.name, 'Test Kingdom')
        self.assertEqual(self.kingdom.description, 'Test Description')
        self.assertIsNotNone(self.kingdom.created_at)
    
    def test_kingdom_str(self):
        """Тест строкового представления королевства"""
        self.assertEqual(str(self.kingdom), 'Test Kingdom')


class TestModelTest(TestCase):
    """Тесты для модели Test"""
    
    def setUp(self):
        self.kingdom = Kingdom.objects.create(name='Test Kingdom')
        self.test = Test.objects.create(
            kingdom=self.kingdom,
            title='Test Title',
            description='Test Description'
        )
    
    def test_test_creation(self):
        """Тест создания теста"""
        self.assertEqual(self.test.title, 'Test Title')
        self.assertEqual(self.test.kingdom, self.kingdom)
        self.assertTrue(self.test.is_active)
    
    def test_test_str(self):
        """Тест строкового представления теста"""
        expected = f"{self.test.title} ({self.kingdom.name})"
        self.assertEqual(str(self.test), expected)


class QuestionModelTest(TestCase):
    """Тесты для модели Question"""
    
    def setUp(self):
        self.kingdom = Kingdom.objects.create(name='Test Kingdom')
        self.test = Test.objects.create(
            kingdom=self.kingdom,
            title='Test Title'
        )
        self.question = Question.objects.create(
            test=self.test,
            text='Test Question?',
            correct_answer=True,
            order=1
        )
    
    def test_question_creation(self):
        """Тест создания вопроса"""
        self.assertEqual(self.question.text, 'Test Question?')
        self.assertTrue(self.question.correct_answer)
        self.assertEqual(self.question.order, 1)
        self.assertEqual(self.question.test, self.test)
    
    def test_question_str(self):
        """Тест строкового представления вопроса"""
        self.assertEqual(str(self.question), 'Test Question?...')


class TestAttemptModelTest(TestCase):
    """Тесты для модели TestAttempt"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='citizen@example.com',
            password='testpass123',
            first_name='Test',
            last_name='Citizen',
            role='citizen'
        )
        self.kingdom = Kingdom.objects.create(name='Test Kingdom')
        self.citizen = Citizen.objects.create(
            user=self.user,
            kingdom=self.kingdom,
            age=25,
            pigeon_email='citizen@example.com'
        )
        self.test = Test.objects.create(
            kingdom=self.kingdom,
            title='Test Title'
        )
        self.attempt = TestAttempt.objects.create(
            citizen=self.citizen,
            test=self.test,
            total_questions=5
        )
    
    def test_attempt_creation(self):
        """Тест создания попытки тестирования"""
        self.assertEqual(self.attempt.citizen, self.citizen)
        self.assertEqual(self.attempt.test, self.test)
        self.assertEqual(self.attempt.total_questions, 5)
        self.assertEqual(self.attempt.status, 'in_progress')
        self.assertEqual(self.attempt.score, 0)
    
    def test_attempt_percentage(self):
        """Тест расчета процента правильных ответов"""
        self.attempt.score = 3
        self.assertEqual(self.attempt.percentage, 60.0)


class AnswerModelTest(TestCase):
    """Тесты для модели Answer"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='citizen@example.com',
            password='testpass123',
            first_name='Test',
            last_name='Citizen',
            role='citizen'
        )
        self.kingdom = Kingdom.objects.create(name='Test Kingdom')
        self.citizen = Citizen.objects.create(
            user=self.user,
            kingdom=self.kingdom,
            age=25,
            pigeon_email='citizen@example.com'
        )
        self.test = Test.objects.create(
            kingdom=self.kingdom,
            title='Test Title'
        )
        self.question = Question.objects.create(
            test=self.test,
            text='Test Question?',
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
            answer=True,
            is_correct=True
        )
    
    def test_answer_creation(self):
        """Тест создания ответа"""
        self.assertEqual(self.answer.attempt, self.attempt)
        self.assertEqual(self.answer.question, self.question)
        self.assertTrue(self.answer.answer)
        self.assertTrue(self.answer.is_correct)
    
    def test_answer_str(self):
        """Тест строкового представления ответа"""
        expected = f"{self.citizen.user.get_full_name()} - Test Question?..."
        self.assertEqual(str(self.answer), expected)


class UserRegistrationTest(TestCase):
    """Тесты регистрации пользователей"""
    
    def setUp(self):
        self.client = Client()
        self.kingdom = Kingdom.objects.create(name='Test Kingdom')
    
    def test_citizen_registration(self):
        """Тест регистрации подданного"""
        data = {
            'email': 'newcitizen@example.com',
            'first_name': 'New',
            'last_name': 'Citizen',
            'role': 'citizen',
            'kingdom': self.kingdom.id,
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        
        response = self.client.post(reverse('users:register'), data)
        self.assertEqual(response.status_code, 302)  # Редирект после успешной регистрации
        
        # Проверяем, что пользователь создан
        user = User.objects.get(email='newcitizen@example.com')
        self.assertEqual(user.role, 'citizen')
        
        # Проверяем, что создан профиль подданного
        citizen = Citizen.objects.get(user=user)
        self.assertEqual(citizen.kingdom, self.kingdom)
    
    def test_king_registration(self):
        """Тест регистрации короля"""
        data = {
            'email': 'newking@example.com',
            'first_name': 'New',
            'last_name': 'King',
            'role': 'king',
            'kingdom': self.kingdom.id,
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        
        response = self.client.post(reverse('users:register'), data)
        self.assertEqual(response.status_code, 302)
        
        # Проверяем, что пользователь создан
        user = User.objects.get(email='newking@example.com')
        self.assertEqual(user.role, 'king')
        
        # Проверяем, что создан профиль короля
        king = King.objects.get(user=user)
        self.assertEqual(king.kingdom, self.kingdom)


class TestTakingTest(TestCase):
    """Тесты прохождения тестирования"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='citizen@example.com',
            password='testpass123',
            first_name='Test',
            last_name='Citizen',
            role='citizen'
        )
        self.kingdom = Kingdom.objects.create(name='Test Kingdom')
        self.citizen = Citizen.objects.create(
            user=self.user,
            kingdom=self.kingdom,
            age=25,
            pigeon_email='citizen@example.com'
        )
        self.test = Test.objects.create(
            kingdom=self.kingdom,
            title='Test Title'
        )
        self.question = Question.objects.create(
            test=self.test,
            text='Test Question?',
            correct_answer=True,
            order=1
        )
    
    def test_start_test(self):
        """Тест начала тестирования"""
        self.client.login(email='citizen@example.com', password='testpass123')
        
        response = self.client.post(reverse('kingdom:start_test'))
        self.assertEqual(response.status_code, 302)
        
        # Проверяем, что создана попытка тестирования
        attempt = TestAttempt.objects.get(citizen=self.citizen, test=self.test)
        self.assertEqual(attempt.status, 'in_progress')
        self.assertEqual(attempt.total_questions, 1)
    
    def test_answer_question(self):
        """Тест ответа на вопрос"""
        self.client.login(email='citizen@example.com', password='testpass123')
        
        # Создаем попытку тестирования
        attempt = TestAttempt.objects.create(
            citizen=self.citizen,
            test=self.test,
            total_questions=1
        )
        
        # Отвечаем на вопрос
        response = self.client.post(
            reverse('kingdom:answer_question', args=[self.question.id]),
            {'answer': 'true'},
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Проверяем, что ответ сохранен
        answer = Answer.objects.get(attempt=attempt, question=self.question)
        self.assertTrue(answer.answer)
        self.assertTrue(answer.is_correct)
        
        # Проверяем, что попытка завершена
        attempt.refresh_from_db()
        self.assertEqual(attempt.status, 'completed')
        self.assertEqual(attempt.score, 1)


class APITest(APITestCase):
    """Тесты для REST API"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role='citizen'
        )
        self.kingdom = Kingdom.objects.create(name='Test Kingdom')
        self.citizen = Citizen.objects.create(
            user=self.user,
            kingdom=self.kingdom,
            age=25,
            pigeon_email='test@example.com'
        )
        
        # Получаем JWT токен
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_user_profile_api(self):
        """Тест API профиля пользователя"""
        response = self.client.get('/api/profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')
    
    def test_kingdoms_api(self):
        """Тест API королевств"""
        response = self.client.get('/api/kingdoms/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Kingdom')
    
    def test_citizens_api(self):
        """Тест API подданных"""
        response = self.client.get('/api/citizens/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['user_name'], 'Test User')
    
    def test_dashboard_api(self):
        """Тест API панели управления"""
        response = self.client.get('/api/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user_type'], 'citizen')
        self.assertIn('citizen', response.data)