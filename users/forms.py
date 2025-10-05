from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import User


class UserRegistrationForm(UserCreationForm):
    """Форма регистрации пользователя"""
    
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите ваш email'
        })
    )
    first_name = forms.CharField(
        label='Имя',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите ваше имя'
        })
    )
    last_name = forms.CharField(
        label='Фамилия',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите вашу фамилию'
        })
    )
    role = forms.ChoiceField(
        label='Роль',
        choices=User.ROLE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'role', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Введите пароль'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Подтвердите пароль'})
    
    def clean_email(self):
        """Проверка уникальности email"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с таким email уже существует')
        return email


class UserLoginForm(forms.Form):
    """Форма входа пользователя"""
    
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите ваш email'
        })
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )
    remember_me = forms.BooleanField(
        label='Запомнить меня',
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )


class UserProfileForm(forms.ModelForm):
    """Форма профиля пользователя"""
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Делаем email только для чтения, так как он используется для входа
        self.fields['email'].widget.attrs['readonly'] = True
        self.fields['email'].help_text = 'Email нельзя изменить'
