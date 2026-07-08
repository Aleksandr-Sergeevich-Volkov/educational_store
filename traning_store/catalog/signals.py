import re

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_save
from django.dispatch import receiver


@receiver(pre_save, sender=User)
def validate_user_before_save(sender, instance, **kwargs):
    """
    Валидация пользователя перед сохранением
    Работает для всех способов создания: форма, админка, shell, API
    """

    config = getattr(settings, 'SPAM_PROTECTION', {})

    if not config.get('ENABLED', True):
        return

    # ==========================================
    # 1. Проверка username
    # ==========================================
    if instance.username:
        patterns = config.get('BANNED_USERNAME_PATTERNS', [])
        for pattern in patterns:
            if re.match(pattern, instance.username):
                raise ValidationError(
                    f'Username "{instance.username}" выглядит как спам. '
                    'Используйте осмысленное имя.'
                )

        if instance.username.isdigit():
            raise ValidationError(
                'Имя пользователя не может состоять только из цифр'
            )

    # ==========================================
    # 2. Проверка email по БЕЛОМУ СПИСКУ
    # ==========================================
    if instance.email:
        allowed_domains = config.get('ALLOWED_EMAIL_DOMAINS', [])

        if not allowed_domains:
            return

        email_domain = instance.email.split('@')[-1].lower()

        if email_domain not in allowed_domains:
            # Формируем красивое сообщение с примерами
            examples = ', '.join(allowed_domains[:5])
            raise ValidationError(
                f'Регистрация с email доменом "{email_domain}" запрещена. '
                f'Используйте email от одного из поддерживаемых провайдеров: '
                f'{examples} и другие.'
            )

    # ==========================================
    # 3. Проверка first_name
    # ==========================================
    if instance.first_name:
        patterns = config.get('BANNED_USERNAME_PATTERNS', [])
        for pattern in patterns:
            if re.match(pattern, instance.first_name.lower()):
                raise ValidationError(
                    f'Имя "{instance.first_name}" выглядит подозрительно'
                )

    # ==========================================
    # 4. Проверка last_name
    # ==========================================
    if instance.last_name:
        patterns = config.get('BANNED_USERNAME_PATTERNS', [])
        for pattern in patterns:
            if re.match(pattern, instance.last_name.lower()):
                raise ValidationError(
                    f'Фамилия "{instance.last_name}" выглядит подозрительно'
                )
