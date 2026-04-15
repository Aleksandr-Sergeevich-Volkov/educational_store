import json
import os

import redis
from django.conf import settings

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=os.getenv('REDIS_PASSWORD'),  # Добавьте эту строку
    decode_responses=True
)

# Время жизни временного выбора (10 минут)
TTL_SELECTION = 600  # 10 * 60 секунд


def get_redis_key(user_id, product_id):
    """Генерирует ключ для Redis"""
    return f"cart_temp:{user_id}:{product_id}"


def set_temp_selection(user_id, product_id, field, value):
    """Сохраняет временный выбор характеристики в Redis"""
    key = get_redis_key(user_id, product_id)

    # Получаем текущие данные
    data = redis_client.get(key)
    selections = json.loads(data) if data else {}

    # Обновляем поле
    selections[field] = value

    # Сохраняем с TTL
    redis_client.setex(key, TTL_SELECTION, json.dumps(selections))
    print(f"📦 Redis сохранено: {key} -> {field}={value}")


def get_temp_selection(user_id, product_id):
    """Получает все выбранные характеристики из Redis"""
    key = get_redis_key(user_id, product_id)
    data = redis_client.get(key)

    if data:
        # Обновляем TTL (продлеваем сессию)
        redis_client.expire(key, TTL_SELECTION)
        return json.loads(data)
    return {}


def clear_temp_selection(user_id, product_id):
    """Очищает временный выбор в Redis"""
    key = get_redis_key(user_id, product_id)
    redis_client.delete(key)
    print(f"🗑 Redis очищено: {key}")


def update_selection_ttl(user_id, product_id):
    """Продлевает время жизни выбора"""
    key = get_redis_key(user_id, product_id)
    if redis_client.exists(key):
        redis_client.expire(key, TTL_SELECTION)
        print(f"🔄 TTL обновлён: {key}")


def set_order_state(user_id, field, value):
    """Сохраняет состояние оформления заказа"""
    key = f"order_temp:{user_id}"
    data = redis_client.get(key)
    order_data = json.loads(data) if data else {}
    order_data[field] = value
    redis_client.setex(key, 3600, json.dumps(order_data))  # 1 час


def get_order_state(user_id):
    """Получает состояние оформления заказа"""
    key = f"order_temp:{user_id}"
    data = redis_client.get(key)
    return json.loads(data) if data else {}


def clear_order_state(user_id):
    """Очищает состояние заказа"""
    key = f"order_temp:{user_id}"
    redis_client.delete(key)
