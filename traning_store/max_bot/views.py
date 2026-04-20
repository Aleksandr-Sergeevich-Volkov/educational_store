"""
Обработка вебхуков от MAX
"""
import json
import logging

from catalog.models import (Class_compress, Color, Gallery, Model_type,
                            Product, Size, Type_product)
from coupons.models import Coupon
from django.db import models
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from orders.models import Order, OrderItem
from orders.tasks import order_created

from traning_store.settings import ROBOKASSA_LOGIN, ROBOKASSA_PASSWORD_1
from traning_store.views import generate_payment_link

from .keyboards import (get_compress_classes_keyboard, get_main_keyboard,
                        get_product_keyboard, get_products_keyboard)
from .messages import (format_product_card, format_product_list,
                       get_start_message)
from .services import CartService, send_message, send_message_with_image
from .state import (clear_order_state, clear_temp_selection, get_order_state,
                    get_temp_selection, save_user_id_for_order,
                    set_order_state, set_temp_selection)

logger = logging.getLogger(__name__)


@csrf_exempt
def max_webhook(request):
    try:
        data = json.loads(request.body)
        update_type = data.get('update_type')
        user_id = None
        text = None
        callback = None
        # 1. bot_started — нажали "Начать"
        if update_type == 'bot_started':
            user_id = data.get('user_id')
            text = '/start'
        # 2. message_created — текстовое сообщение
        elif update_type == 'message_created':
            message_data = data.get('message', {})
            sender = message_data.get('sender', {})
            user_id = sender.get('user_id')
            body = message_data.get('body', {})
            text = body.get('text', '')
        # 3. message_callback — нажатие на кнопку
        elif update_type == 'message_callback':
            # Получаем объект callback
            callback_obj = data.get('callback') or data.get('message', {}).get('body', {}).get('callback')
            callback_payload = None
            user_id = None

            if callback_obj and isinstance(callback_obj, dict):
                # Извлекаем payload и user_id из объекта callback
                callback_payload = callback_obj.get('payload')
                user_id = callback_obj.get('user', {}).get('user_id')
                print(f"🔘 Callback payload: {callback_payload} from user {user_id}")
            else:
                # Fallback: ищем в других местах
                callback_payload = data.get('payload') or data.get('callback')
                user_id = data.get('user_id') or data.get('message', {}).get('sender', {}).get('user_id')

            # Если user_id всё ещё ID бота, пробуем другой вариант
            if user_id == 228090361 and callback_obj:
                user_id = callback_obj.get('user', {}).get('user_id')

            print(f"👤 Final user_id: {user_id}")
            print(f"🔘 Final callback: {callback_payload}")

            # Сохраняем для дальнейшей обработки
            callback = callback_payload

        order_state = get_order_state(user_id)
        step = order_state.get('step')

        if step and text and not text.startswith('/'):
            if step == 'first_name':
                checkout_process_first_name(user_id, text)
            elif step == 'last_name':
                checkout_process_last_name(user_id, text)
            elif step == 'email':
                checkout_process_email(user_id, text)
            elif step == 'yandex_address':
                checkout_process_address(user_id, text, 'yandex')
            elif step == 'cdek_address':
                checkout_process_address(user_id, text, 'cdek')
            elif step == 'coupon_code':
                apply_coupon_code(user_id, text)
            else:
                send_message(user_id, "Неизвестная команда")
            return JsonResponse({"ok": True})

        # Обработка
        if callback:
            handle_callback(user_id, callback)
        elif text == '/start':
            send_welcome(user_id)
        elif text == '/help':
            send_message(user_id, "❓ Помощь в разработке")
        else:
            send_message(user_id, "Неизвестная команда. Используйте /help")
        return JsonResponse({"ok": True})  # ← ВАЖНО: возвращаем ответ!

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({"ok": False, "error": str(e)}, status=500)


def get_products_with_main_images(queryset):
    """Добавляет главные изображения к queryset товаров"""
    return queryset.prefetch_related(
        models.Prefetch(
            'images',
            queryset=Gallery.objects.filter(main=True),
            to_attr='main_images'
        )
    )


def send_products_with_photos(user_id, products, title):
    """Отправляет список товаров, каждый с фото."""
    # ===== ОТЛАДКА: считаем количество товаров =====
    print("🔍 send_products_with_photos called")
    print(f"   Title: {title}")
    print(f"   Products exists: {products.exists()}")
    print(f"   Products count: {products.count()}")
    if not products.exists():
        send_message(user_id, f"😔 {title} не найдены")
        return
    # Отправляем заголовок категории
    send_message(user_id, f"🛍 *{title}*")
    # ===== ОТЛАДКА: выводим каждый товар =====
    for idx, product in enumerate(products):
        print(f"   Product {idx}: id={product.id}, name={product.name[:30]}, stock={product.stock}")

        # Получаем фото
        image_url = None
        if hasattr(product, 'main_images') and product.main_images:
            image_url = product.main_images[0].image.url
            if image_url.startswith('/'):
                image_url = f"https://kompressionnye-chulki24.ru{image_url}"
            print(f"      Image URL: {image_url}")
        else:
            print("No main_images attribute or empty")

        # Формируем текст
        text = f"*{product.name[:40]}*\n"
        text += f"  💰 {product.price:,.0f} ₽ | 📦 {'В наличии' if product.stock > 0 else 'Под заказ'}\n"
        text += f"  🆔 {product.articul}"

        # Кнопка для просмотра
        buttons = [[
            {"type": "callback", "text": "🔍 Подробнее", "payload": f"product_{product.id}"}
        ]]

        # ===== ОТЛАДКА: что отправляем =====
        print(f"      Sending message for product {product.id}")

        if image_url:
            send_message_with_image(user_id, text, image_url, {"buttons": buttons})
        else:
            send_message(user_id, text, {"buttons": buttons})

    # Кнопка "Назад"
    print("   Sending back button")
    send_message(user_id, "◀️ Навигация", {"buttons": [[{"type": "callback", "text": "◀️ Назад к категориям", "payload": "back"}]]})
    print("✅ send_products_with_photos completed")


def send_welcome(user_id):
    """Отправляет приветственное сообщение"""
    print(f"send_welcome called for user_id={user_id}")
    from .services import send_message
    text = get_start_message()
    buttons = get_main_keyboard()
    print(f"Welcome text: {text[:50]}...")
    print(f"Buttons: {buttons}")

    result = send_message(user_id, text, buttons)
    print(f"send_message_result_: {result}")


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
    """Показывает товары по категории — каждый с фото"""
    products_qs = Product.objects.filter(
        Type_product_id=category_id,
        available=True
    )[:10]
    # print(f'products_qs: {products_qs}')
    products = get_products_with_main_images(products_qs)
    # print(f'products: {products}')
    category = Type_product.objects.filter(id=category_id).first()
    category_name = category.name if category else "выбранной категории"
    if not products.exists():
        send_message(user_id, f"В категории «{category_name}» пока нет товаров")
        return
    # Отправляем заголовок
    send_message(user_id, f"🛍 *{category_name}*")
    # Отправляем каждый товар с фото
    for product in products:
        # Получаем URL фото
        image_url = None
        if hasattr(product, 'main_images') and product.main_images:
            # print(f"image_url_!_@_: {product.main_images[0].image.url}")
            image_url = product.main_images[0].image.url
            if image_url.startswith('/'):
                image_url = f"https://kompressionnye-chulki24.ru{image_url}"
        # Формируем текст
        text = f"*{product.name[:50]}*\n"
        text += f"💰 *Цена:* {product.price:,.0f} ₽\n"
        text += f"📦 *Наличие:* {'В наличии' if product.stock > 0 else 'Под заказ'}\n"
        text += f"🏷 *Артикул:* {product.articul}"
        # Кнопка для просмотра
        buttons = {"buttons": [[{"type": "callback", "text": "🔍 Подробнее", "payload": f"product_{product.id}"}]]}
        if image_url:
            send_message_with_image(user_id, text, image_url, buttons)
        else:
            send_message(user_id, text, {"buttons": buttons})
    # Кнопка "Назад"
    send_message(user_id, "◀️ Навигация", [[{"type": "callback", "text": "◀️ Назад к категориям", "payload": "back_to_categories"}]])


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


# ========== КОРЗИНА ==========

def show_cart(user_id):
    """Показывает содержимое корзины"""
    cart = CartService(user_id)
    items = cart.get_items()

    if cart.is_empty():
        send_message(user_id, "🛒 *Ваша корзина пуста*\n\nДобавьте товары через карточку товара")
        return

    text = "🛒 *Ваша корзина:*\n\n"
    buttons = []

    for idx, item in enumerate(items, 1):  # ← нумерация с 1
        subtotal = item.get_total_price()
        text += f"{idx}. *{item.get_display_name()}*\n"
        text += f"   {item.quantity} шт × {item.price_at_add:,.0f} ₽ = {subtotal:,.0f} ₽\n\n"

        buttons.append([
            {"type": "callback", "text": f"❌ Удалить # {idx}", "payload": f"cart_remove_{item.id}"}
        ])

    text += f"💰 *Итого:* {cart.get_total_price():,.0f} ₽"

    buttons.append([
        {"type": "callback", "text": "➕ Продолжить покупки", "payload": "catalog"},
        {"type": "callback", "text": "Применить купон", "payload": "coupon"},
        {"type": "callback", "text": "📝 Оформить заказ", "payload": "checkout"}
    ])
    send_message(user_id, text, buttons)

# ========== ДОБАВЛЕНИЕ В КОРЗИНУ (С ВЫБОРОМ ХАРАКТЕРИСТИК) ==========


def apply_coupon_code(user_id, coupon_id):
    now = timezone.now()
    try:
        coupon = Coupon.objects.get(code__iexact=coupon_id,
                                    valid_from__lte=now,
                                    valid_to__gte=now,
                                    active=True)
        cart = CartService(user_id)
        cart.set_coupon(coupon.id)

        discount = cart.get_discount()
        total = cart.get_total_price()
        total_with_discount = total

        text = f"✅ *Промокод {coupon.code} применён!*\n\n"
        text += f"💰 Скидка: {coupon.discount}%\n"
        text += f"📉 Сумма скидки: {discount:,.0f} ₽\n"
        text += f"💵 Итого к оплате: {total_with_discount:,.0f} ₽\n\n"
        text += "🛒 /cart — посмотреть корзину"

        send_message(user_id, text)

    except Coupon.DoesNotExist:
        send_message(user_id, "❌ *Неверный или просроченный промокод*\n\nПопробуйте другой код")

    clear_order_state(user_id)


def add_to_cart_start(user_id, product_id):
    """Начало процесса добавления в корзину — выбор размера"""
    product = Product.objects.get(id=product_id, available=True)

    # Очищаем предыдущие временные выборы
    clear_temp_selection(user_id, product_id)

    # Получаем доступные размеры для этого бренда
    sizes = Size.objects.filter(brand=product.brand)

    if sizes.exists():
        buttons = []
        for size in sizes:
            buttons.append([
                {"type": "callback", "text": size.name, "payload": f"select_size_{product_id}_{size.id}"}
            ])
        send_message(user_id, "📏 *Выберите размер:*", buttons)
    else:
        # Если размеров нет, сохраняем None и переходим к цвету
        set_temp_selection(user_id, product_id, 'size', None)
        add_to_cart_select_color(user_id, product_id)


def add_to_cart_select_color(user_id, product_id):
    """Шаг 2: выбор цвета"""
    product = Product.objects.get(id=product_id)
    colors = product.Color.all()

    if colors.exists():
        buttons = []
        for color in colors:
            buttons.append([
                {"type": "callback", "text": color.name, "payload": f"select_color_{product_id}_{color.id}"}
            ])
        send_message(user_id, "🎨 *Выберите цвет:*", buttons)
    else:
        set_temp_selection(user_id, product_id, 'color', None)
        add_to_cart_select_model_type(user_id, product_id)


def add_to_cart_select_model_type(user_id, product_id):
    """Шаг 3: выбор типа модели"""
    product = Product.objects.get(id=product_id)
    model_types = Model_type.objects.filter(brand=product.brand)

    if model_types.exists():
        buttons = []
        for mt in model_types:
            buttons.append([
                {"type": "callback", "text": mt.name, "payload": f"select_model_{product_id}_{mt.id}"}
            ])
        send_message(user_id, "📦 *Выберите тип модели:*", buttons)
    else:
        set_temp_selection(user_id, product_id, 'model_type', None)
        add_to_cart_select_quantity(user_id, product_id)


def add_to_cart_select_quantity(user_id, product_id):
    """Шаг 4: выбор количества"""
    buttons = []
    for i in [1, 2, 3, 4, 5]:
        buttons.append([
            {"type": "callback", "text": str(i), "payload": f"select_quantity_{product_id}_{i}"}])
    send_message(user_id, "🔢 *Выберите количество:*", buttons)


def add_to_cart_finalize(user_id, product_id, quantity):
    """Финальное добавление в корзину"""
    product = Product.objects.get(id=product_id, available=True)
    selections = get_temp_selection(user_id, product_id)

    # Получаем объекты характеристик
    size = Size.objects.get(id=selections.get('size')) if selections.get('size') else None
    color = Color.objects.get(id=selections.get('color')) if selections.get('color') else None
    model_type = Model_type.objects.get(id=selections.get('model_type')) if selections.get('model_type') else None

    # Добавляем в корзину
    cart = CartService(user_id)
    cart.add(
        product=product,
        quantity=quantity,
        size=size,
        color=color,
        model_type=model_type
    )

    # Очищаем временные данные из Redis
    clear_temp_selection(user_id, product_id)
    buttons = []
    buttons.append([
        {"type": "callback", "text": "Посмотреть корзину", "payload": "cart"},
    ])

    send_message(user_id, f"✅ *{product.name[:40]}*\n\nДобавлен в корзину_!_\n\n🛒", buttons)


def remove_from_cart_handler(user_id, cart_item_id):
    """Удаление товара из корзины"""
    cart = CartService(user_id)
    cart.remove(cart_item_id)
    send_message(user_id, "🗑 Товар удалён из корзины")
    show_cart(user_id)


# max_bot/views.py

def checkout_start(user_id):
    """Начало оформления заказа"""
    cart = CartService(user_id)

    if cart.is_empty():
        send_message(user_id, "🛒 *Корзина пуста*\n\nДобавьте товары перед оформлением")
        return

    clear_order_state(user_id)

    total = cart.get_total_price()

    text = "📝 *Оформление заказа*\n\n"
    text += f"💰 *Сумма заказа:* {total:,.0f} ₽\n\n"
    text += "👤 *Введите ваше имя:*"

    set_order_state(user_id, 'step', 'first_name')
    send_message(user_id, text)


def checkout_process_first_name(user_id, text):
    """Обработка ввода имени"""
    if len(text.strip()) < 2:
        send_message(user_id, "❌ *Введите корректное имя* (не менее 2 символов)")
        return

    set_order_state(user_id, 'first_name', text.strip())
    set_order_state(user_id, 'step', 'last_name')
    send_message(user_id, "👤 *Введите вашу фамилию:*")


def checkout_process_last_name(user_id, text):
    """Обработка ввода фамилии"""
    if len(text.strip()) < 2:
        send_message(user_id, "❌ *Введите корректную фамилию* (не менее 2 символов)")
        return

    set_order_state(user_id, 'last_name', text.strip())
    set_order_state(user_id, 'step', 'email')
    send_message(user_id, "📧 *Введите ваш email:*\n\nПример: name@example.com")


def checkout_process_email(user_id, text):
    """Обработка ввода email"""
    if '@' not in text or '.' not in text:
        send_message(user_id, "❌ *Неверный формат email*\n\nПример: name@example.com")
        return
    set_order_state(user_id, 'email', text.strip())
    set_order_state(user_id, 'step', 'delivery_type')

    # Выбор способа доставки
    keyboard = [
               [{"type": "callback", "text": "📦 Яндекс Доставка", "payload": "delivery_yandex"}],
               [{"type": "callback", "text": "📮 СДЭК", "payload": "delivery_cdek"}]]
    send_message(user_id, "🚚 *Выберите способ доставки:*", keyboard)


def checkout_process_delivery(user_id, delivery_type):
    """Обработка выбора доставки"""
    set_order_state(user_id, 'delivery_type', delivery_type)

    if delivery_type == 'yandex':
        set_order_state(user_id, 'step', 'yandex_address')
        send_message(
            user_id,
            "📍 *Введите адрес пункта выдачи Яндекс:*\n\n"
            "Пример адреса: г. Москва, ул. Тверская, д. 1"
        )

    elif delivery_type == 'cdek':
        set_order_state(user_id, 'step', 'cdek_address')
        send_message(
            user_id,
            "📍 *Введите адрес пункта выдачи СДЭК:*\n\n"
            "Пример: г. Москва, ул. Тверская, д. 1"
        )


def checkout_process_address(user_id, text, delivery_type):
    """Обработка ввода адреса/ID ПВЗ"""
    set_order_state(user_id, 'address_pvz', text.strip())
    checkout_confirm(user_id)


def checkout_confirm(user_id):
    """Подтверждение заказа (без расчёта доставки)"""
    state = get_order_state(user_id)
    cart = CartService(user_id)
    items = cart.get_items()

    total = cart.get_total_price()

    # Формируем текст для подтверждения
    text = "📝 *Проверьте данные заказа:*\n\n"
    text += f"👤 *Имя:* {state.get('first_name')} {state.get('last_name')}\n"
    text += f"📧 *Email:* {state.get('email')}\n"
    text += f"🚚 *Доставка:* {state.get('delivery_type')}\n"
    text += f"📍 *Адрес/ПВЗ:* {state.get('address_pvz')}\n\n"

    text += "📦 *Товары:*\n"
    for item in items:
        text += f"• {item.get_display_name()}\n"
        text += f"  {item.quantity} шт × {item.price_at_add:,.0f} ₽\n"

    text += f"\n💰 *Итого:* {total:,.0f} ₽\n"
    text += "🚚 *Доставка:* от 500 рублей бесплатно\n\n"
    text += "✅ Для подтверждения заказа нажмите кнопку ниже"

    keyboard = [
               [{"type": "callback", "text": "✅ Подтвердить заказ", "payload": "order_confirm"}],
               [{"type": "callback", "text": "❌ Отменить", "payload": "order_cancel"}]]

    set_order_state(user_id, 'step', 'confirm')
    send_message(user_id, text, keyboard)


def checkout_finalize(user_id):
    """Сохранение заказа в БД"""
    state = get_order_state(user_id)
    cart = CartService(user_id)
    items = cart.get_items()

    if not items:
        send_message(user_id, "❌ Корзина пуста")
        return

    # Создаём заказ
    order = Order.objects.create(
        first_name=state.get('first_name', ''),
        last_name=state.get('last_name', ''),
        email=state.get('email', ''),
        delivery_type=state.get('delivery_type', ''),
        address_pvz=state.get('address_pvz', ''),
        delivery_sum=0,  # без расчёта
        paid=False
    )

    # Создаём позиции заказа
    for item in items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            price=item.price_at_add,
            quantity=item.quantity,
            size=item.size,
            color=item.color,
            m_type=item.model_type
        )
    save_user_id_for_order(order.id, user_id)
    # Очищаем корзину и состояние
    cart.clear()
    clear_order_state(user_id)

    # ========== ВЫЗЫВАЕМ ЗАДАЧУ ДЛЯ ОТПРАВКИ EMAIL ==========
    try:
        order_created.delay(order.id)  # ← асинхронно через Celery
        email_status = "отправлено"
    except Exception as e:
        print(f"Failed to send email: {e}")
        email_status = "не отправлено (ошибка)"

    # Отправляем подтверждение в бот
    text = f"✅ *Заказ #{order.id} оформлен!*\n\n"
    text += f"📧 Письмо с подтверждением {email_status} на {state.get('email')}\n"
    text += "📞 Менеджер свяжется с вами для уточнения деталей\n\n"
    text += "Спасибо за покупку!"
    keyboard = [[{"type": "callback", "text": "💳 Оплатить заказ", "payload": f"order_pay_{order.id}"}],
                [{"type": "callback", "text": "🛍 Продолжить покупки", "payload": "catalog"}]]
    send_message(user_id, text, keyboard)

    # Уведомление администратору
    admin_text = f"🆕 *Новый заказ #{order.id}*\n"
    admin_text += f"👤 {state.get('first_name')} {state.get('last_name')}\n"
    admin_text += f"📧 {state.get('email')}\n"
    admin_text += f"🚚 {state.get('delivery_type')}\n"
    admin_text += f"📍 {state.get('address_pvz')}\n"
    admin_text += f"💰 Сумма: {order.get_total_cost():,.0f} ₽"
    send_message(10817976, admin_text)  # раскомментировать, если есть ID админа


def pay(user_id, order_id):
    order = get_object_or_404(Order, id=order_id)
    text = generate_payment_link(
        merchant_login=ROBOKASSA_LOGIN,
        merchant_password_1=ROBOKASSA_PASSWORD_1,
        cost=order.get_total_cost(),
        number=order.id,
        description='kompressionnyj_trikotazh',
        is_test=0,
        robokassa_payment_url='https://auth.robokassa.ru/Merchant/Index.aspx',
        email=order.email,
    )
    send_message(user_id, text)


def handle_callback(user_id, callback):
    """
    Обработка нажатий на кнопки.
    callback — это строка (payload), например 'catalog'
    """
    print(f"🔵 handle_callback: user_id={user_id}, callback={callback}")
    # Если callback пришёл как словарь, извлекаем payload
    if isinstance(callback, dict):
        callback = callback.get('payload')
        print(f"   Extracted payload: {callback}")
    if not callback or not isinstance(callback, str):
        print("Invalid callback format")
        send_message(user_id, "Ошибка обработки кнопки")
        return
    # Обработка
    if callback == 'catalog':
        print("🟢 Showing catalog categories")
        show_catalog_categories(user_id)
    elif callback == 'search':
        send_message(user_id, "🔍 Введите название товара для поиска")

    # ========== КОРЗИНА ==========
    elif callback == 'cart':
        show_cart(user_id)

    elif callback.startswith('cart_remove_'):
        cart_item_id = callback.split('_')[2]
        remove_from_cart_handler(user_id, cart_item_id)
        # ========== ДОБАВЛЕНИЕ В КОРЗИНУ (пошагово) ==========
    elif callback.startswith('add_to_cart_'):
        product_id = callback.split('_')[3]
        add_to_cart_start(user_id, product_id)

    elif callback.startswith('select_size_'):
        parts = callback.split('_')
        product_id = parts[2]
        size_id = parts[3]
        set_temp_selection(user_id, product_id, 'size', size_id)
        add_to_cart_select_color(user_id, product_id)

    elif callback.startswith('select_color_'):
        parts = callback.split('_')
        product_id = parts[2]
        color_id = parts[3]
        set_temp_selection(user_id, product_id, 'color', color_id)
        add_to_cart_select_model_type(user_id, product_id)

    elif callback.startswith('select_model_'):
        parts = callback.split('_')
        product_id = parts[2]
        model_id = parts[3]
        set_temp_selection(user_id, product_id, 'model_type', model_id)
        add_to_cart_select_quantity(user_id, product_id)

    elif callback.startswith('select_quantity_'):
        parts = callback.split('_')
        product_id = parts[2]
        quantity = int(parts[3])
        add_to_cart_finalize(user_id, product_id, quantity)
    elif callback == 'contacts':
        send_message(user_id, "📞 Контакты: +7 (906) 717-48-77")
    elif callback == 'help':
        send_message(user_id, "❓ Помощь в разработке")
    elif callback == 'back':
        send_welcome(user_id)
    elif callback == 'back_to_categories':
        show_catalog_categories(user_id)
    elif callback == 'back_to_products':
        show_catalog_categories(user_id)
    elif callback.startswith('category_'):
        category_id = callback.split('_')[1]
        show_products_by_category(user_id, category_id)
    elif callback.startswith('product_'):
        product_id = callback.split('_')[1]
        show_product_detail(user_id, product_id)
    elif callback == 'checkout':
        checkout_start(user_id)

    elif callback == 'delivery_yandex':
        checkout_process_delivery(user_id, 'yandex')

    elif callback == 'delivery_cdek':
        checkout_process_delivery(user_id, 'cdek')

    elif callback == 'order_confirm':
        checkout_finalize(user_id)

    elif callback == 'order_cancel':
        clear_order_state(user_id)
        send_message(user_id, "❌ Оформление заказа отменено")

    elif callback == 'coupon':
        set_order_state(user_id, 'step', 'coupon_code')
        send_message(user_id, "🎫 *Введите промокод:*\n\nНапример: SUMMER10")

    elif callback.startswith('order_pay_'):
        # Извлекаем order_id из callback
        order_id = callback.split('_')[2]  # "order_pay_42" → ["order", "pay", "42"] → "42"
        pay(user_id, order_id)
    else:
        send_message(user_id, f"Неизвестная команда: {callback}")
