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
        export_order = ('id', 'name', 'description', 'created_at', 'updated_at')


class KingResource(resources.ModelResource):
    """Ресурс для импорта/экспорта королей"""
    
    class Meta:
        model = King
        fields = ('id', 'user__email', 'kingdom__name', 'max_citizens', 'created_at', 'updated_at')
        export_order = ('id', 'user__email', 'kingdom__name', 'max_citizens', 'created_at', 'updated_at')


class CitizenResource(resources.ModelResource):
    """Ресурс для импорта/экспорта подданных"""
    
    class Meta:
        model = Citizen
        fields = ('id', 'user__email', 'kingdom__name', 'age', 'pigeon_email', 'is_enrolled', 'created_at')
        export_order = ('id', 'user__email', 'kingdom__name', 'age', 'pigeon_email', 'is_enrolled', 'created_at')


class TestResource(resources.ModelResource):
    """Ресурс для импорта/экспорта тестов"""
    
    class Meta:
        model = Test
        fields = ('id', 'title', 'description', 'kingdom__name', 'is_active', 'created_at', 'updated_at')
        export_order = ('id', 'title', 'description', 'kingdom__name', 'is_active', 'created_at', 'updated_at')


class QuestionResource(resources.ModelResource):
    """Ресурс для импорта/экспорта вопросов"""
    
    class Meta:
        model = Question
        fields = ('id', 'text', 'test__title', 'correct_answer', 'order', 'created_at', 'updated_at')
        export_order = ('id', 'text', 'test__title', 'correct_answer', 'order', 'created_at', 'updated_at')


class TestAttemptResource(resources.ModelResource):
    """Ресурс для импорта/экспорта попыток прохождения тестов"""
    
    class Meta:
        model = TestAttempt
        fields = ('id', 'citizen__user__email', 'test__title', 'status', 'score', 'started_at', 'completed_at')
        export_order = ('id', 'citizen__user__email', 'test__title', 'status', 'score', 'started_at', 'completed_at')


class AnswerResource(resources.ModelResource):
    """Ресурс для импорта/экспорта ответов"""
    
    class Meta:
        model = Answer
        fields = ('id', 'attempt__citizen__user__email', 'question__text', 'answer', 'is_correct', 'answered_at')
        export_order = ('id', 'attempt__citizen__user__email', 'question__text', 'answer', 'is_correct', 'answered_at')
