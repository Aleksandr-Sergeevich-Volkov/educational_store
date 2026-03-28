"""
Клавиатуры для бота MAX
"""


def get_main_keyboard():
    return {
        "buttons": [  # ← ключ "buttons"
            [
                {"text": "🛍 Каталог", "callback": "catalog"},
                {"text": "🔍 Поиск", "callback": "search"}
            ],
            [
                {"text": "📦 Корзина", "callback": "cart"},
                {"text": "📞 Контакты", "callback": "contacts"}
            ],
            [
                {"text": "❓ Помощь", "callback": "help"}
            ]
        ]
    }


def get_categories_keyboard(categories):
    """Клавиатура с категориями товаров (виды изделий)"""
    keyboard = []
    row = []
    for i, cat in enumerate(categories):
        row.append({"text": cat.name, "callback_data": f"category_{cat.id}"})
        if len(row) == 2 or i == len(categories) - 1:
            keyboard.append(row)
            row = []

    keyboard.append([{"text": "◀️ Назад", "callback_data": "back"}])
    return {"inline_keyboard": keyboard}


def get_compress_classes_keyboard(classes):
    """Клавиатура с классами компрессии"""
    keyboard = []
    for cls in classes:
        keyboard.append([{"text": cls.name, "callback_data": f"compress_{cls.id}"}])

    keyboard.append([{"text": "◀️ Назад", "callback_data": "back"}])

    return {"inline_keyboard": keyboard}


def get_products_keyboard(products):
    """Клавиатура со списком товаров"""
    keyboard = []
    for product in products[:10]:
        text = f"{product.name[:30]} - {product.price} ₽"
        keyboard.append([{"text": text, "callback_data": f"product_{product.id}"}])

    keyboard.append([{"text": "⬅️ Назад", "callback_data": "back"}])

    return {"inline_keyboard": keyboard}


def get_product_keyboard(product_id):
    """Клавиатура для карточки товара"""
    return {
        "inline_keyboard": [
            [
                {"text": "🛒 В корзину", "callback_data": f"add_to_cart_{product_id}"},
                {"text": "❤️ В избранное", "callback_data": f"favorite_{product_id}"}
            ],
            [
                {"text": "📏 Таблица размеров", "callback_data": f"size_table_{product_id}"}
            ],
            [
                {"text": "◀️ Назад к каталогу", "callback_data": "back_to_catalog"}
            ]
        ]
    }
