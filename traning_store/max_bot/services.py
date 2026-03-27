"""
Сервисы для отправки сообщений в MAX API
"""
import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

MAX_API_URL = "https://platform-api.max.ru/messages"


def send_message(user_id, text, keyboard=None):
    """
    Отправляет сообщение пользователю через MAX API.

    Args:
        user_id (str): ID пользователя в MAX
        text (str): Текст сообщения (можно с Markdown)
        keyboard (dict, optional): Inline-клавиатура

    Returns:
        bool: True если отправлено успешно
    """
    if not settings.MAX_BOT_TOKEN:
        logger.error("MAX_BOT_TOKEN не настроен в settings.py")
        return False

    headers = {
        "Authorization": settings.MAX_BOT_TOKEN,
        "Content-Type": "application/json"
    }

    payload = {"text": text}
    if keyboard:
        payload["keyboard"] = keyboard

    try:
        response = requests.post(
            f"{MAX_API_URL}?user_id={user_id}",
            json=payload,
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            logger.info(f"Message sent to {user_id}")
            return True
        else:
            logger.error(f"Failed to send message: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return False
