from django import forms
from django.core.exceptions import ValidationError
from .models import Kingdom, Citizen, TestAttempt, Answer


class KingdomSelectionForm(forms.Form):
    """Форма выбора королевства при регистрации"""
    
    kingdom = forms.ModelChoiceField(
        queryset=Kingdom.objects.all(),
        empty_label="Выберите королевство",
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Королевство'
    )


class CitizenProfileForm(forms.ModelForm):
    """Форма профиля подданного"""
    
    class Meta:
        model = Citizen
        fields = ('age', 'pigeon_email')
        widgets = {
            'age': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '150',
                'placeholder': 'Введите ваш возраст'
            }),
            'pigeon_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите email для голубя'
            }),
        }
        labels = {
            'age': 'Возраст',
            'pigeon_email': 'Голубь (email)',
        }
    
    def clean_age(self):
        """Проверка возраста"""
        age = self.cleaned_data.get('age')
        if age and (age < 1 or age > 150):
            raise ValidationError('Возраст должен быть от 1 до 150 лет')
        return age


class TestAnswerForm(forms.Form):
    """Форма ответа на вопрос теста"""
    
    def __init__(self, question, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.question = question
        
        self.fields['answer'] = forms.ChoiceField(
            choices=[
                (True, 'Да'),
                (False, 'Нет'),
            ],
            widget=forms.RadioSelect(attrs={
                'class': 'form-check-input'
            }),
            label=question.text,
            required=True
        )
    
    def save(self, attempt):
        """Сохранение ответа"""
        answer_value = self.cleaned_data['answer']
        is_correct = answer_value == self.question.correct_answer
        
        answer, created = Answer.objects.get_or_create(
            attempt=attempt,
            question=self.question,
            defaults={
                'answer': answer_value,
                'is_correct': is_correct,
            }
        )
        
        if not created:
            answer.answer = answer_value
            answer.is_correct = is_correct
            answer.save()
        
        return answer


class TestAttemptForm(forms.ModelForm):
    """Форма начала тестирования"""
    
    class Meta:
        model = TestAttempt
        fields = ('test',)
        widgets = {
            'test': forms.HiddenInput(),
        }
    
    def __init__(self, citizen, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.citizen = citizen
        
        # Получаем тест для королевства подданного
        try:
            test = citizen.kingdom.test
            self.fields['test'].initial = test
            self.fields['test'].widget = forms.HiddenInput()
        except Test.DoesNotExist:
            raise ValidationError('Для вашего королевства не создано тестовое испытание')
    
    def save(self, commit=True):
        """Сохранение попытки тестирования"""
        attempt = super().save(commit=False)
        attempt.citizen = self.citizen
        attempt.total_questions = attempt.test.questions.count()
        
        if commit:
            attempt.save()
        
        return attempt
