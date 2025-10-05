from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.views import LoginView
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
import logging

from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm
from .models import User
from action_logs.models import ActionLog
from kingdom.models import Kingdom, Citizen, King

logger = logging.getLogger('users')


class HomeView(TemplateView):
    """Главная страница с формой авторизации и регистрации"""
    template_name = 'users/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['login_form'] = UserLoginForm()
        context['registration_form'] = UserRegistrationForm()
        context['kingdoms'] = Kingdom.objects.all()
        return context


class UserRegistrationView(CreateView):
    """Представление регистрации пользователя"""
    model = User
    form_class = UserRegistrationForm
    template_name = 'users/registration.html'
    success_url = reverse_lazy('users:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['kingdoms'] = Kingdom.objects.all()
        return context
    
    def form_valid(self, form):
        """Обработка валидной формы"""
        user = form.save()
        
        # Создаем профиль в зависимости от роли
        kingdom = Kingdom.objects.get(id=self.request.POST.get('kingdom'))
        
        if user.role == 'citizen':
            Citizen.objects.create(
                user=user,
                kingdom=kingdom,
                age=0,  # Будет заполнено позже
                pigeon_email=user.email or f"{user.username}@example.com"
            )
        elif user.role == 'king':
            King.objects.create(
                user=user,
                kingdom=kingdom
            )
        
        # Логируем регистрацию
        ActionLog.objects.create(
            user=user,
            action='register',
            description=f'Регистрация пользователя {user.get_full_name()}',
            ip_address=self.get_client_ip(),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
        
        logger.info(f'Пользователь {user.email} зарегистрирован с ролью {user.role}')
        
        messages.success(self.request, 'Регистрация прошла успешно! Теперь вы можете войти в систему.')
        return redirect(self.success_url)
    
    def get_client_ip(self):
        """Получение IP адреса клиента"""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class UserLoginView(LoginView):
    """Представление входа пользователя"""
    template_name = 'users/login.html'
    form_class = UserLoginForm
    redirect_authenticated_user = True
    
    def get_success_url(self):
        """Определение URL для перенаправления после входа"""
        user = self.request.user
        
        # Логируем вход
        ActionLog.objects.create(
            user=user,
            action='login',
            description=f'Вход пользователя {user.get_full_name()}',
            ip_address=self.get_client_ip(),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
        
        logger.info(f'Пользователь {user.username} вошел в систему')
        
        # Перенаправляем в зависимости от роли
        if user.is_king:
            return reverse_lazy('kingdom:king_dashboard')
        elif user.is_citizen:
            return reverse_lazy('kingdom:citizen_dashboard')
        else:
            return reverse_lazy('users:profile')
    
    def get_client_ip(self):
        """Получение IP адреса клиента"""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


@method_decorator(login_required, name='dispatch')
class UserProfileView(TemplateView):
    """Представление профиля пользователя"""
    template_name = 'users/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        context['user'] = user
        context['profile_form'] = UserProfileForm(instance=user)
        
        # Добавляем дополнительную информацию в зависимости от роли
        if user.is_king:
            try:
                context['king_profile'] = user.king_profile
            except King.DoesNotExist:
                pass
        elif user.is_citizen:
            try:
                context['citizen_profile'] = user.citizen_profile
            except Citizen.DoesNotExist:
                pass
        
        return context


@login_required
def update_profile(request):
    """Обновление профиля пользователя"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
        else:
            messages.error(request, 'Ошибка при обновлении профиля.')
    
    return redirect('users:profile')


@login_required
def user_logout(request):
    """Выход пользователя"""
    user = request.user
    
    # Логируем выход
    ActionLog.objects.create(
        user=user,
        action='logout',
        description=f'Выход пользователя {user.get_full_name()}',
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    logger.info(f'Пользователь {user.email} вышел из системы')
    
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы.')
    return redirect('users:home')


def get_client_ip(request):
    """Получение IP адреса клиента"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@csrf_exempt
@require_http_methods(["POST"])
def api_login(request):
    """API для входа пользователя"""
    try:
        data = request.POST
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return JsonResponse({'error': 'Email и пароль обязательны'}, status=400)
        
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                
                # Логируем вход
                ActionLog.objects.create(
                    user=user,
                    action='login',
                    description=f'API вход пользователя {user.get_full_name()}',
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                return JsonResponse({
                    'success': True,
                    'user': {
                        'id': str(user.id),
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'role': user.role,
                    }
                })
            else:
                return JsonResponse({'error': 'Аккаунт неактивен'}, status=400)
        else:
            return JsonResponse({'error': 'Неверные учетные данные'}, status=400)
    
    except Exception as e:
        logger.error(f'Ошибка API входа: {str(e)}')
        return JsonResponse({'error': 'Внутренняя ошибка сервера'}, status=500)