from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
import logging

from users.models import User
from action_logs.models import ActionLog
from .serializers import UserSerializer, UserRegistrationSerializer, UserLoginSerializer

logger = logging.getLogger('users')


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
