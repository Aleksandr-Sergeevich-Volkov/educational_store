"""
Обработка вебхуков от MAX
"""
import json
import logging

from catalog.models import Class_compress, Product, Type_product
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from .keyboards import (get_compress_classes_keyboard, get_main_keyboard,
                        get_product_keyboard, get_products_keyboard)
from .messages import (format_product_card, format_product_list,
                       get_start_message)
from .services import send_message

# from django.views.decorators.http import require_POST


logger = logging.getLogger(__name__)


@csrf_exempt
def max_webhook(request):
    """
    Эндпоинт для получения вебхуков от MAX.
    """
    print("=" * 60)
    print("WEBHOOK CALLED")
    print(f"Method: {request.method}")
    print(f"Body: {request.body}")
    print("=" * 60)

    try:
        data = json.loads(request.body)

        # Извлекаем данные из реальной структуры MAX
        message = data.get('message', {})
        sender = message.get('sender', {})
        user_id = sender.get('user_id')  # ← user_id отправителя

        body = message.get('body', {})
        text = body.get('text', '')

        # callback может приходить в другом поле
        callback = data.get('callback') or data.get('payload')

        print(f"user_id: {user_id}, text: {text}, callback: {callback}")

        if not user_id:
            return JsonResponse({"ok": False, "error": "user_id required"}, status=400)

        # Обработка нажатия на кнопку
        if callback:
            handle_callback(user_id, callback)

        # Обработка текстовых команд
        elif text == '/start':
            send_welcome(user_id)

        elif text == '/help':
            send_message(user_id, "Помощь в разработке")

        else:
            send_message(user_id, "Неизвестная команда. Используйте /help")

        return JsonResponse({"ok": True})

    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return JsonResponse({"ok": False, "error": "Invalid JSON"}, status=400)

    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({"ok": False, "error": str(e)}, status=500)


def send_welcome(user_id):
    """Отправляет приветственное сообщение"""
    from .services import send_message

    text = get_start_message()
    buttons = get_main_keyboard()  # ← теперь buttons
    send_message(user_id, text, buttons)


def show_catalog_categories(user_id):
    """Показывает категории товаров (виды изделий)"""
    from .keyboards import get_categories_keyboard
    from .services import send_message

    categories = Type_product.objects.all()
    if categories.exists():
        text = "Выберите вид изделия:"
        buttons = get_categories_keyboard(categories)
        send_message(user_id, text, buttons)
    else:
        send_message(user_id, "Категории временно недоступны")


def show_compress_classes(user_id):
    """Показывает классы компрессии для фильтрации"""
    classes = Class_compress.objects.all()

    if classes.exists():
        text = "Выберите класс компрессии:"
        keyboard = get_compress_classes_keyboard(classes)
        send_message(user_id, text, keyboard)
    else:
        send_message(user_id, "Классы компрессии временно недоступны")


def show_all_products(user_id):
    """Показывает все товары в наличии"""
    products = Product.objects.filter(available=True, stock__gt=0)[:20]

    if products.exists():
        text = format_product_list(products)
        keyboard = get_products_keyboard(products)
        send_message(user_id, text, keyboard)
    else:
        send_message(user_id, "Товары временно недоступны")


def show_products_by_category(user_id, category_id):
    """Показывает товары по категории (виду изделия)"""
    products = Product.objects.filter(
        Type_product_id=category_id,
        available=True
    )[:20]

    category = Type_product.objects.filter(id=category_id).first()
    category_name = category.name if category else "выбранной категории"

    if products.exists():
        text = format_product_list(products, f"🛍 {category_name}")
        keyboard = get_products_keyboard(products)
        send_message(user_id, text, keyboard)
    else:
        send_message(user_id, f"В категории «{category_name}» пока нет товаров")


def show_products_by_compress(user_id, compress_id):
    """Показывает товары по классу компрессии"""
    compress_class = Class_compress.objects.filter(id=compress_id).first()
    compress_name = compress_class.name if compress_class else f"{compress_id} класс"

    products = Product.objects.filter(
        Class_compress_id=compress_id,
        available=True
    )[:20]

    if products.exists():
        text = format_product_list(products, f"📊 {compress_name} компрессии")
        keyboard = get_products_keyboard(products)
        send_message(user_id, text, keyboard)
    else:
        send_message(user_id, f"Товары с {compress_name} компрессии временно отсутствуют")


def show_product_detail(user_id, product_id):
    """Показывает детальную карточку товара"""
    product = get_object_or_404(Product, id=product_id, available=True)

    text = format_product_card(product)
    keyboard = get_product_keyboard(product_id)

    send_message(user_id, text, keyboard)


def search_products(user_id, query):
    """Поиск товаров по запросу"""
    products = Product.objects.filter(
        name__icontains=query,
        available=True
    )[:10]

    if products.exists():
        text = format_product_list(products, f"🔍 Результаты поиска: «{query}»")
        keyboard = get_products_keyboard(products)
        send_message(user_id, text, keyboard)
    else:
        send_message(user_id, f"😔 По запросу «{query}» ничего не найдено")


def handle_callback(user_id, callback):
    """Обработка нажатий на кнопки"""
    print(f"handle_callback: user_id={user_id}, callback={callback}")

    if callback == 'catalog':
        show_catalog_categories(user_id)
    elif callback == 'search':
        send_message(user_id, "🔍 Введите название товара для поиска")
    elif callback == 'cart':
        send_message(user_id, "🛒 Корзина пуста")
    elif callback == 'contacts':
        send_message(user_id, "📞 Контакты: +7 (906) 717-48-77")
    elif callback == 'help':
        send_message(user_id, "❓ Помощь в разработке")
    elif callback == 'back':
        send_welcome(user_id)
    elif callback.startswith('category_'):
        category_id = callback.split('_')[1]
        show_products_by_category(user_id, category_id)
    elif callback.startswith('product_'):
        product_id = callback.split('_')[1]
        show_product_detail(user_id, product_id)
    else:
        send_message(user_id, f"Неизвестная команда: {callback}")
