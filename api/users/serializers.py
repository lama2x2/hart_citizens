from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils import timezone
import logging

from users.models import User, ActionLog
from kingdom.models import Kingdom, Citizen, King

logger = logging.getLogger('users')


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User"""
    
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'role', 'date_joined', 'last_login')
        read_only_fields = ('id', 'date_joined', 'last_login')


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    kingdom_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'role', 'password', 'password_confirm', 'kingdom_id')
    
    def validate(self, attrs):
        """Валидация данных"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Пароли не совпадают")
        
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует")
        
        return attrs
    
    def create(self, validated_data):
        """Создание пользователя"""
        kingdom_id = validated_data.pop('kingdom_id')
        password_confirm = validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        try:
            kingdom = Kingdom.objects.get(id=kingdom_id)
        except Kingdom.DoesNotExist:
            raise serializers.ValidationError("Королевство не найдено")
        
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        
        # Создаем профиль в зависимости от роли
        if user.role == 'citizen':
            Citizen.objects.create(
                user=user,
                kingdom=kingdom,
                age=0,  # Будет заполнено позже
                pigeon_email=user.email
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
            description=f'API регистрация пользователя {user.get_full_name()}',
            ip_address=self.context['request'].META.get('REMOTE_ADDR', ''),
            user_agent=self.context['request'].META.get('HTTP_USER_AGENT', '')
        )
        
        logger.info(f'API регистрация пользователя {user.email} с ролью {user.role}')
        
        return user


class UserLoginSerializer(serializers.Serializer):
    """Сериализатор для входа пользователя"""
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        """Валидация учетных данных"""
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise serializers.ValidationError('Неверные учетные данные')
            if not user.is_active:
                raise serializers.ValidationError('Аккаунт неактивен')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Email и пароль обязательны')
        
        return attrs
