"""
Сервисы для отправки сообщений в MAX API
"""
import json
import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

MAX_API_URL = "https://platform-api.max.ru/messages"


def send_message(user_id, text, buttons=None):
    """Отправляет сообщение пользователю через MAX API"""
    print(f"send_message: user_id={user_id}")
    print(f"text: {text[:50]}...")
    print(f"buttons: {buttons}")

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

    print(f"Payload: {json.dumps(payload, ensure_ascii=False, indent=2)}")

    url = f"https://platform-api.max.ru/messages?user_id={user_id}"

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending message: {e}")
        return False
