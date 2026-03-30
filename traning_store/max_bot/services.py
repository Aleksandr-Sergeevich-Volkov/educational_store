"""
Сервисы для отправки сообщений в MAX API
"""
import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

MAX_API_URL = "https://platform-api.max.ru/messages"


def send_message(user_id, text, buttons=None):
    """
    Отправляет сообщение пользователю через MAX API.
    buttons — список списков кнопок, где каждая кнопка:
        {"type": "callback", "text": "...", "payload": "..."}
    """
    headers = {
        "Authorization": settings.MAX_BOT_TOKEN,
        "Content-Type": "application/json"
    }

    payload = {"text": text}

    if buttons:
        payload["attachments"] = [
            {
                "type": "inline_keyboard",
                "payload": {"buttons": buttons}
            }
        ]

    url = f"https://platform-api.max.ru/messages?user_id={user_id}"

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending message: {e}")
        return False
