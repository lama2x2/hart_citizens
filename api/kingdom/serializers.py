from rest_framework import serializers, status, viewsets, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q
import logging

from kingdom.models import (
    Kingdom, King, Citizen, Test, Question, 
    TestAttempt, Answer
)
from action_logs.models import ActionLog
from users.models import User

logger = logging.getLogger('kingdom')


class KingdomSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Kingdom"""
    
    class Meta:
        model = Kingdom
        fields = ('id', 'name', 'description', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class KingSerializer(serializers.ModelSerializer):
    """Сериализатор для модели King"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    kingdom_name = serializers.CharField(source='kingdom.name', read_only=True)
    current_citizens_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = King
        fields = ('id', 'user_name', 'kingdom_name', 'max_citizens', 'current_citizens_count', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at', 'current_citizens_count')


class CitizenSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Citizen"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    kingdom_name = serializers.CharField(source='kingdom.name', read_only=True)
    king_name = serializers.CharField(source='king.user.get_full_name', read_only=True)
    
    class Meta:
        model = Citizen
        fields = ('id', 'user_name', 'kingdom_name', 'age', 'pigeon_email', 'is_enrolled', 'king_name', 'enrolled_at', 'created_at', 'updated_at')
        read_only_fields = ('id', 'is_enrolled', 'king_name', 'enrolled_at', 'created_at', 'updated_at')


class QuestionSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Question"""
    
    class Meta:
        model = Question
        fields = ('id', 'text', 'order', 'created_at')
        read_only_fields = ('id', 'created_at')


class TestSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Test"""
    kingdom_name = serializers.CharField(source='kingdom.name', read_only=True)
    questions = QuestionSerializer(many=True, read_only=True)
    questions_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Test
        fields = ('id', 'title', 'description', 'kingdom_name', 'is_active', 'questions', 'questions_count', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at', 'questions_count')


class AnswerSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Answer"""
    question_text = serializers.CharField(source='question.text', read_only=True)
    
    class Meta:
        model = Answer
        fields = ('id', 'question_text', 'answer', 'is_correct', 'answered_at')
        read_only_fields = ('id', 'question_text', 'is_correct', 'answered_at')


class TestAttemptSerializer(serializers.ModelSerializer):
    """Сериализатор для модели TestAttempt"""
    citizen_name = serializers.CharField(source='citizen.user.get_full_name', read_only=True)
    test_title = serializers.CharField(source='test.title', read_only=True)
    answers = AnswerSerializer(many=True, read_only=True)
    percentage = serializers.FloatField(read_only=True)
    
    class Meta:
        model = TestAttempt
        fields = ('id', 'citizen_name', 'test_title', 'status', 'score', 'total_questions', 'percentage', 'started_at', 'completed_at', 'answers')
        read_only_fields = ('id', 'citizen_name', 'test_title', 'score', 'total_questions', 'percentage', 'started_at', 'completed_at')


class ActionLogSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ActionLog"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    
    class Meta:
        model = ActionLog
        fields = ('id', 'user_name', 'action', 'action_display', 'description', 'metadata', 'ip_address', 'created_at')
        read_only_fields = ('id', 'user_name', 'action_display', 'created_at')
