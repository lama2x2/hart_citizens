from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from .models import ActionLog
from .utils import log_user_action, log_login, log_logout, log_registration

User = get_user_model()


class ActionLogModelTest(TestCase):
    """Тесты для модели ActionLog"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role='citizen'
        )
    
    def test_action_log_creation(self):
        """Тест создания лога действия"""
        log = ActionLog.objects.create(
            user=self.user,
            action='login',
            description='Test login',
            metadata={'test': 'data'}
        )
        
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.action, 'login')
        self.assertEqual(log.description, 'Test login')
        self.assertEqual(log.metadata, {'test': 'data'})
        self.assertIsNotNone(log.created_at)
    
    def test_action_log_str(self):
        """Тест строкового представления лога"""
        log = ActionLog.objects.create(
            user=self.user,
            action='login',
            description='Test login'
        )
        
        expected_str = f"{self.user.get_full_name()} - Вход в систему ({log.created_at.strftime('%d.%m.%Y %H:%M')})"
        self.assertEqual(str(log), expected_str)


class ActionLogUtilsTest(TestCase):
    """Тесты для утилит логирования"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role='citizen'
        )
    
    def test_log_user_action(self):
        """Тест логирования действия пользователя"""
        log_user_action(
            user=self.user,
            action='login',
            description='Test login',
            metadata={'test': 'data'}
        )
        
        log = ActionLog.objects.get(user=self.user, action='login')
        self.assertEqual(log.description, 'Test login')
        self.assertEqual(log.metadata, {'test': 'data'})
    
    def test_log_login(self):
        """Тест логирования входа"""
        log_login(self.user)
        
        log = ActionLog.objects.get(user=self.user, action='login')
        self.assertIn('Вход пользователя', log.description)
    
    def test_log_logout(self):
        """Тест логирования выхода"""
        log_logout(self.user)
        
        log = ActionLog.objects.get(user=self.user, action='logout')
        self.assertIn('Выход пользователя', log.description)
    
    def test_log_registration(self):
        """Тест логирования регистрации"""
        log_registration(self.user)
        
        log = ActionLog.objects.get(user=self.user, action='register')
        self.assertIn('Регистрация пользователя', log.description)
        self.assertEqual(log.metadata['role'], 'citizen')
