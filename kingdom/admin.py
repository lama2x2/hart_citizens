from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from .models import (
    Kingdom, King, Citizen, Test, Question, 
    TestAttempt, Answer
)


class KingdomResource(resources.ModelResource):
    """Ресурс для импорта/экспорта королевств"""
    
    class Meta:
        model = Kingdom
        fields = ('id', 'name', 'description', 'created_at', 'updated_at')


@admin.register(Kingdom)
class KingdomAdmin(ImportExportModelAdmin):
    """Админка для модели Kingdom"""
    
    resource_class = KingdomResource
    list_display = ('name', 'description_short', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'description')
    ordering = ('name',)
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    def description_short(self, obj):
        """Короткое описание"""
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    description_short.short_description = 'Описание'


class KingResource(resources.ModelResource):
    """Ресурс для импорта/экспорта королей"""
    
    class Meta:
        model = King
        fields = ('id', 'user__email', 'kingdom__name', 'max_citizens', 'created_at', 'updated_at')


@admin.register(King)
class KingAdmin(ImportExportModelAdmin):
    """Админка для модели King"""
    
    resource_class = KingResource
    list_display = ('user_name', 'kingdom_name', 'max_citizens', 'current_citizens_count', 'created_at')
    list_filter = ('created_at', 'max_citizens')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'kingdom__name')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at', 'updated_at', 'current_citizens_count')
    
    def user_name(self, obj):
        """Имя пользователя"""
        return obj.user.get_full_name()
    user_name.short_description = 'Король'
    
    def kingdom_name(self, obj):
        """Название королевства"""
        return obj.kingdom.name
    kingdom_name.short_description = 'Королевство'


class CitizenResource(resources.ModelResource):
    """Ресурс для импорта/экспорта подданных"""
    
    class Meta:
        model = Citizen
        fields = ('id', 'user__email', 'kingdom__name', 'age', 'pigeon_email', 'is_enrolled', 'created_at')


@admin.register(Citizen)
class CitizenAdmin(ImportExportModelAdmin):
    """Админка для модели Citizen"""
    
    resource_class = CitizenResource
    list_display = ('user_name', 'kingdom_name', 'age', 'pigeon_email', 'is_enrolled', 'king_name', 'created_at')
    list_filter = ('is_enrolled', 'kingdom', 'created_at', 'enrolled_at')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'pigeon_email', 'kingdom__name')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at', 'updated_at', 'enrolled_at')
    
    def user_name(self, obj):
        """Имя пользователя"""
        return obj.user.get_full_name()
    user_name.short_description = 'Подданный'
    
    def kingdom_name(self, obj):
        """Название королевства"""
        return obj.kingdom.name
    kingdom_name.short_description = 'Королевство'
    
    def king_name(self, obj):
        """Имя короля"""
        return obj.king.user.get_full_name() if obj.king else '-'
    king_name.short_description = 'Король'


class QuestionInline(admin.TabularInline):
    """Инлайн для вопросов"""
    model = Question
    extra = 1
    ordering = ('order',)


@admin.register(Test)
class TestAdmin(ImportExportModelAdmin):
    """Админка для модели Test"""
    
    list_display = ('title', 'kingdom_name', 'is_active', 'questions_count', 'created_at')
    list_filter = ('is_active', 'created_at', 'kingdom')
    search_fields = ('title', 'description', 'kingdom__name')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at', 'updated_at')
    inlines = [QuestionInline]
    
    def kingdom_name(self, obj):
        """Название королевства"""
        return obj.kingdom.name
    kingdom_name.short_description = 'Королевство'
    
    def questions_count(self, obj):
        """Количество вопросов"""
        return obj.questions.count()
    questions_count.short_description = 'Вопросов'


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Админка для модели Question"""
    
    list_display = ('text_short', 'test_title', 'correct_answer', 'order', 'created_at')
    list_filter = ('correct_answer', 'test__kingdom', 'created_at')
    search_fields = ('text', 'test__title', 'test__kingdom__name')
    ordering = ('test', 'order', 'created_at')
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    def text_short(self, obj):
        """Короткий текст вопроса"""
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_short.short_description = 'Вопрос'
    
    def test_title(self, obj):
        """Название теста"""
        return obj.test.title
    test_title.short_description = 'Тест'


class AnswerInline(admin.TabularInline):
    """Инлайн для ответов"""
    model = Answer
    extra = 0
    readonly_fields = ('question', 'answer', 'is_correct', 'answered_at')


@admin.register(TestAttempt)
class TestAttemptAdmin(admin.ModelAdmin):
    """Админка для модели TestAttempt"""
    
    list_display = ('citizen_name', 'test_title', 'status', 'score', 'total_questions', 'percentage', 'started_at')
    list_filter = ('status', 'test__kingdom', 'started_at', 'completed_at')
    search_fields = ('citizen__user__first_name', 'citizen__user__last_name', 'test__title')
    ordering = ('-started_at',)
    readonly_fields = ('id', 'started_at', 'completed_at', 'percentage')
    inlines = [AnswerInline]
    
    def citizen_name(self, obj):
        """Имя подданного"""
        return obj.citizen.user.get_full_name()
    citizen_name.short_description = 'Подданный'
    
    def test_title(self, obj):
        """Название теста"""
        return obj.test.title
    test_title.short_description = 'Тест'


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    """Админка для модели Answer"""
    
    list_display = ('attempt_citizen', 'question_short', 'answer', 'is_correct', 'answered_at')
    list_filter = ('is_correct', 'answered_at', 'question__test__kingdom')
    search_fields = ('attempt__citizen__user__first_name', 'attempt__citizen__user__last_name', 'question__text')
    ordering = ('-answered_at',)
    readonly_fields = ('id', 'answered_at')
    
    def attempt_citizen(self, obj):
        """Подданный из попытки"""
        return obj.attempt.citizen.user.get_full_name()
    attempt_citizen.short_description = 'Подданный'
    
    def question_short(self, obj):
        """Короткий текст вопроса"""
        return obj.question.text[:50] + '...' if len(obj.question.text) > 50 else obj.question.text
    question_short.short_description = 'Вопрос'