from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'

urlpatterns = [
    # Главная страница
    path('', views.HomeView.as_view(), name='home'),
    
    # Аутентификация
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    
    # Профиль
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    
    # API
    path('api/login/', views.api_login, name='api_login'),
]
