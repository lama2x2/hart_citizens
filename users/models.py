import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    """Менеджер для кастомной модели пользователя"""
    
    def create_user(self, email, password=None, **extra_fields):
        """Создание обычного пользователя"""
        if not email:
            raise ValueError('Email обязателен')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Создание суперпользователя"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Суперпользователь должен иметь is_superuser=True')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Кастомная модель пользователя"""
    
    ROLE_CHOICES = [
        ('king', 'Король'),
        ('citizen', 'Подданный'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, verbose_name='Email')
    first_name = models.CharField(max_length=150, verbose_name='Имя')
    last_name = models.CharField(max_length=150, verbose_name='Фамилия')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, verbose_name='Роль')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    is_staff = models.BooleanField(default=False, verbose_name='Персонал')
    is_superuser = models.BooleanField(default=False, verbose_name='Суперпользователь')
    date_joined = models.DateTimeField(default=timezone.now, verbose_name='Дата регистрации')
    last_login = models.DateTimeField(blank=True, null=True, verbose_name='Последний вход')
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'role']
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        db_table = 'users'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    def get_full_name(self):
        """Возвращает полное имя пользователя"""
        return f"{self.first_name} {self.last_name}"
    
    def get_short_name(self):
        """Возвращает короткое имя пользователя"""
        return self.first_name
    
    @property
    def is_king(self):
        """Проверяет, является ли пользователь королем"""
        return self.role == 'king'
    
    @property
    def is_citizen(self):
        """Проверяет, является ли пользователь подданным"""
        return self.role == 'citizen'