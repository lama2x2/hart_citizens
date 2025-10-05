from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from .models import User


class UserRegistrationForm(UserCreationForm):
    """Форма регистрации пользователя"""
    
    username = forms.CharField(
        label='Username',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите ваш username'
        })
    )
    email = forms.EmailField(
        label='Email (только для подданных)',
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите ваш email (опционально)'
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
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Введите пароль'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Подтвердите пароль'})
    
    def clean_email(self):
        """Валидация email"""
        email = self.cleaned_data.get('email')
        role = self.cleaned_data.get('role')
        
        # Email обязателен только для подданных
        if role == 'citizen' and not email:
            raise ValidationError('Email обязателен для подданных')
        
        if email and User.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с таким email уже существует')
        return email
    
    def clean_username(self):
        """Валидация username"""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('Пользователь с таким username уже существует')
        return username


class UserLoginForm(AuthenticationForm):
    """Форма входа пользователя"""
    
    username = forms.CharField(
        label='Username',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите ваш username'
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
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Введите ваш username'})
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Введите пароль'})


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
