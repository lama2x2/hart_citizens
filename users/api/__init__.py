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


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """API регистрации пользователя"""
    serializer = UserRegistrationSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        user = serializer.save()
        
        # Генерируем JWT токены
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """API входа пользователя"""
    serializer = UserLoginSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # Генерируем JWT токены
        refresh = RefreshToken.for_user(user)
        
        # Логируем вход
        ActionLog.objects.create(
            user=user,
            action='login',
            description=f'API вход пользователя {user.get_full_name()}',
            ip_address=request.META.get('REMOTE_ADDR', ''),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        logger.info(f'API вход пользователя {user.email}')
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    """API получения профиля пользователя"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """API обновления профиля пользователя"""
    serializer = UserSerializer(
        request.user, 
        data=request.data, 
        partial=request.method == 'PATCH'
    )
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """API выхода пользователя"""
    try:
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        # Логируем выход
        ActionLog.objects.create(
            user=request.user,
            action='logout',
            description=f'API выход пользователя {request.user.get_full_name()}',
            ip_address=request.META.get('REMOTE_ADDR', ''),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        logger.info(f'API выход пользователя {request.user.email}')
        
        return Response({'message': 'Выход выполнен успешно'}, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f'Ошибка при выходе: {str(e)}')
        return Response({'error': 'Ошибка при выходе'}, status=status.HTTP_400_BAD_REQUEST)
