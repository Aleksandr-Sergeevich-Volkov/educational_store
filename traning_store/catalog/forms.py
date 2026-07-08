import re

# forms.py
from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        max_length=64,
        label='Почта',
        required=True,
        help_text='Обязательное поле. Введите действующий email.'
    )
    first_name = forms.CharField(required=False, max_length=32, label='Имя')
    last_name = forms.CharField(required=False, max_length=32, label='Фамилия')

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if not username:
            raise forms.ValidationError('Имя пользователя обязательно')

        # Проверка на спам-паттерны
        config = getattr(settings, 'SPAM_PROTECTION', {})
        patterns = config.get('BANNED_USERNAME_PATTERNS', [])

        for pattern in patterns:
            if re.match(pattern, username):
                raise forms.ValidationError(
                    f'Имя пользователя "{username}" выглядит как спам. '
                    'Используйте осмысленное имя.'
                )

        if username.isdigit():
            raise forms.ValidationError(
                'Имя пользователя не может состоять только из цифр'
            )

        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if not email:
            raise forms.ValidationError('Поле "Почта" обязательно для заполнения')

        # Проверка по белому списку
        config = getattr(settings, 'SPAM_PROTECTION', {})
        allowed_domains = config.get('ALLOWED_EMAIL_DOMAINS', [])

        if allowed_domains:
            email_domain = email.split('@')[-1].lower()
            if email_domain not in allowed_domains:
                examples = ', '.join(allowed_domains[:5])
                raise forms.ValidationError(
                    f'Регистрация с email доменом "{email_domain}" запрещена. '
                    f'Используйте email от одного из поддерживаемых провайдеров: '
                    f'{examples} и другие.'
                )

        # Проверка на существующий email
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Эта почта уже зарегистрирована')

        return email

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')

        if first_name:
            config = getattr(settings, 'SPAM_PROTECTION', {})
            patterns = config.get('BANNED_USERNAME_PATTERNS', [])

            for pattern in patterns:
                if re.match(pattern, first_name.lower()):
                    raise forms.ValidationError(
                        f'Имя "{first_name}" выглядит подозрительно'
                    )

        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')

        if last_name:
            config = getattr(settings, 'SPAM_PROTECTION', {})
            patterns = config.get('BANNED_USERNAME_PATTERNS', [])

            for pattern in patterns:
                if re.match(pattern, last_name.lower()):
                    raise forms.ValidationError(
                        f'Фамилия "{last_name}" выглядит подозрительно'
                    )

        return last_name

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        labels = {
            'username': 'Логин',
            'email': 'Почта',
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'password1': 'Пароль',
            'password2': 'Повторить пароль'
        }

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})


class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username',)
