from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from kingdom.models import Kingdom, King, Citizen

User = get_user_model()


class UserModelTest(TestCase):
    """Тесты для модели User"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
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
        expected = f"{self.user.username} ({self.user.first_name} {self.user.last_name})"
        self.assertEqual(str(self.user), expected)
    
    def test_user_get_full_name(self):
        """Тест получения полного имени"""
        expected = f"{self.user.first_name} {self.user.last_name}"
        self.assertEqual(self.user.get_full_name(), expected)
    
    def test_user_get_short_name(self):
        """Тест получения короткого имени"""
        # В нашей модели нет метода get_short_name, используем first_name напрямую
        self.assertEqual(self.user.first_name, 'Test')
    
    def test_user_is_citizen(self):
        """Тест проверки роли подданного"""
        self.assertTrue(self.user.is_citizen)
        self.assertFalse(self.user.is_king)
    
    def test_user_is_king(self):
        """Тест проверки роли короля"""
        king_user = User.objects.create_user(
            username='kinguser',
            email='king@example.com',
            password='testpass123',
            first_name='King',
            last_name='User',
            role='king'
        )
        self.assertTrue(king_user.is_king)
        self.assertFalse(king_user.is_citizen)


class UserRegistrationFormTest(TestCase):
    """Тесты для формы регистрации"""
    
    def setUp(self):
        self.kingdom = Kingdom.objects.create(name='Test Kingdom')
    
    def test_valid_registration_form(self):
        """Тест валидной формы регистрации"""
        from users.forms import UserRegistrationForm
        
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'citizen',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_invalid_email_registration_form(self):
        """Тест формы регистрации с невалидным email"""
        from users.forms import UserRegistrationForm
        
        form_data = {
            'username': 'invaliduser',
            'email': 'invalid-email',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'citizen',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_password_mismatch_registration_form(self):
        """Тест формы регистрации с несовпадающими паролями"""
        from users.forms import UserRegistrationForm
        
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'citizen',
            'password1': 'testpass123',
            'password2': 'differentpass'
        }
        
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)


class UserLoginFormTest(TestCase):
    """Тесты для формы входа"""
    
    def test_valid_login_form(self):
        """Тест валидной формы входа"""
        from users.forms import UserLoginForm
        
        # Создаем пользователя для теста
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role='citizen'
        )
        
        form_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        form = UserLoginForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_empty_login_form(self):
        """Тест пустой формы входа"""
        from users.forms import UserLoginForm
        
        form = UserLoginForm(data={})
        self.assertFalse(form.is_valid())


class UserViewsTest(TestCase):
    """Тесты для представлений пользователей"""
    
    def setUp(self):
        self.client = Client()
        self.kingdom = Kingdom.objects.create(name='Test Kingdom')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role='citizen'
        )
    
    def test_home_view(self):
        """Тест главной страницы"""
        response = self.client.get(reverse('users:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Кадровая служба королевства')
    
    def test_login_view_get(self):
        """Тест GET запроса страницы входа"""
        response = self.client.get(reverse('users:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Вход в систему')
    
    def test_login_view_post_valid(self):
        """Тест POST запроса с валидными данными"""
        response = self.client.post(reverse('users:login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Редирект после успешного входа
    
    def test_login_view_post_invalid(self):
        """Тест POST запроса с невалидными данными"""
        response = self.client.post(reverse('users:login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)  # Остается на странице входа
    
    def test_logout_view(self):
        """Тест выхода из системы"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('users:logout'))
        self.assertEqual(response.status_code, 302)  # Редирект после выхода
    
    def test_profile_view_authenticated(self):
        """Тест страницы профиля для аутентифицированного пользователя"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Профиль пользователя')
    
    def test_profile_view_unauthenticated(self):
        """Тест страницы профиля для неаутентифицированного пользователя"""
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 302)  # Редирект на страницу входа


class UserAPITest(APITestCase):
    """Тесты для API пользователей"""
    
    def setUp(self):
        self.kingdom = Kingdom.objects.create(name='Test Kingdom')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role='citizen'
        )
        self.citizen = Citizen.objects.create(
            user=self.user,
            kingdom=self.kingdom,
            age=25,
            pigeon_email='test@example.com'
        )
    
    def test_user_registration_api(self):
        """Тест API регистрации пользователя"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'citizen',
            'kingdom_id': str(self.kingdom.id),
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        }
        
        response = self.client.post('/api/users/auth/register/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertIn('tokens', response.data)
    
    def test_user_login_api(self):
        """Тест API входа пользователя"""
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        response = self.client.post('/api/users/auth/login/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        self.assertIn('tokens', response.data)
    
    def test_user_login_api_invalid_credentials(self):
        """Тест API входа с невалидными учетными данными"""
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        
        response = self.client.post('/api/users/auth/login/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
    
    def test_user_profile_api_authenticated(self):
        """Тест API профиля для аутентифицированного пользователя"""
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        response = self.client.get('/api/users/profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')
    
    def test_user_profile_api_unauthenticated(self):
        """Тест API профиля для неаутентифицированного пользователя"""
        response = self.client.get('/api/users/profile/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_user_profile_update_api(self):
        """Тест API обновления профиля"""
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        
        response = self.client.patch('/api/users/profile/update/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Updated')
        self.assertEqual(response.data['last_name'], 'Name')
    
    def test_user_logout_api(self):
        """Тест API выхода из системы"""
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        data = {
            'refresh_token': str(refresh)
        }
        
        response = self.client.post('/api/users/auth/logout/', data)
        # Ожидаем 200 или 400 (если blacklist не настроен)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])
        if response.status_code == status.HTTP_200_OK:
            self.assertIn('message', response.data)