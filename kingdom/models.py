import uuid
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Kingdom(models.Model):
    """Модель королевства"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True, verbose_name='Наименование королевства')
    description = models.TextField(blank=True, verbose_name='Описание')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Королевство'
        verbose_name_plural = 'Королевства'
        db_table = 'kingdoms'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class King(models.Model):
    """Модель короля"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='king_profile'
    )
    kingdom = models.OneToOneField(
        Kingdom,
        on_delete=models.CASCADE,
        verbose_name='Королевство',
        related_name='king'
    )
    max_citizens = models.PositiveIntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name='Максимальное количество подданных'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Король'
        verbose_name_plural = 'Короли'
        db_table = 'kings'
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.kingdom.name}"
    
    @property
    def current_citizens_count(self):
        """Возвращает текущее количество подданных"""
        return self.citizens.count()
    
    @property
    def can_accept_more_citizens(self):
        """Проверяет, может ли король принять больше подданных"""
        return self.current_citizens_count < self.max_citizens


class Citizen(models.Model):
    """Модель подданного"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='citizen_profile'
    )
    kingdom = models.ForeignKey(
        Kingdom,
        on_delete=models.CASCADE,
        verbose_name='Королевство',
        related_name='citizens'
    )
    age = models.PositiveIntegerField(verbose_name='Возраст')
    pigeon_email = models.EmailField(verbose_name='Голубь (email)')
    is_enrolled = models.BooleanField(default=False, verbose_name='Зачислен')
    enrolled_at = models.DateTimeField(blank=True, null=True, verbose_name='Дата зачисления')
    king = models.ForeignKey(
        King,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Король',
        related_name='citizens'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Подданный'
        verbose_name_plural = 'Подданные'
        db_table = 'citizens'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.kingdom.name})"
    
    def enroll(self, king):
        """Зачисляет подданного к королю"""
        if not king.can_accept_more_citizens:
            raise ValueError(f"Король {king.user.get_full_name()} не может принять больше подданных")
        
        self.is_enrolled = True
        self.king = king
        self.enrolled_at = timezone.now()
        self.save()


class Test(models.Model):
    """Модель тестового испытания"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    kingdom = models.OneToOneField(
        Kingdom,
        on_delete=models.CASCADE,
        verbose_name='Королевство',
        related_name='test'
    )
    title = models.CharField(max_length=200, verbose_name='Название испытания')
    description = models.TextField(blank=True, verbose_name='Описание')
    is_active = models.BooleanField(default=True, verbose_name='Активно')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Тестовое испытание'
        verbose_name_plural = 'Тестовые испытания'
        db_table = 'tests'
    
    def __str__(self):
        return f"{self.title} ({self.kingdom.name})"


class Question(models.Model):
    """Модель вопроса тестового испытания"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        verbose_name='Тестовое испытание',
        related_name='questions'
    )
    text = models.TextField(verbose_name='Текст вопроса')
    correct_answer = models.BooleanField(verbose_name='Правильный ответ')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        db_table = 'questions'
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"{self.text[:50]}..."


class TestAttempt(models.Model):
    """Модель попытки прохождения теста"""
    
    STATUS_CHOICES = [
        ('in_progress', 'В процессе'),
        ('completed', 'Завершен'),
        ('failed', 'Не пройден'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    citizen = models.ForeignKey(
        Citizen,
        on_delete=models.CASCADE,
        verbose_name='Подданный',
        related_name='test_attempts'
    )
    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        verbose_name='Тестовое испытание',
        related_name='attempts'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='in_progress',
        verbose_name='Статус'
    )
    score = models.PositiveIntegerField(default=0, verbose_name='Баллы')
    total_questions = models.PositiveIntegerField(default=0, verbose_name='Всего вопросов')
    started_at = models.DateTimeField(auto_now_add=True, verbose_name='Начато')
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name='Завершено')
    
    class Meta:
        verbose_name = 'Попытка прохождения теста'
        verbose_name_plural = 'Попытки прохождения тестов'
        db_table = 'test_attempts'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.citizen.user.get_full_name()} - {self.test.title}"
    
    @property
    def wrong_answers(self):
        """Возвращает количество неправильных ответов"""
        return self.total_questions - self.score
    
    @property
    def percentage(self):
        """Возвращает процент правильных ответов"""
        if self.total_questions == 0:
            return 0
        return round((self.score / self.total_questions) * 100, 2)


class Answer(models.Model):
    """Модель ответа на вопрос"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    attempt = models.ForeignKey(
        TestAttempt,
        on_delete=models.CASCADE,
        verbose_name='Попытка',
        related_name='answers'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        verbose_name='Вопрос',
        related_name='answers'
    )
    answer = models.BooleanField(verbose_name='Ответ')
    is_correct = models.BooleanField(verbose_name='Правильный ответ')
    answered_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата ответа')
    
    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'
        db_table = 'answers'
        unique_together = ['attempt', 'question']
    
    def __str__(self):
        return f"{self.attempt.citizen.user.get_full_name()} - {self.question.text[:30]}..."
    
    def save(self, *args, **kwargs):
        """Автоматически заполняем is_correct на основе ответа и правильного ответа вопроса"""
        if self.is_correct is None:
            self.is_correct = self.answer == self.question.correct_answer
        super().save(*args, **kwargs)