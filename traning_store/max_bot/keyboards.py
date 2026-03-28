"""
Клавиатуры для бота MAX
"""


def get_main_keyboard():
    """Главная клавиатура"""
    return {
        "buttons": [
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
    buttons = []
    for cat in categories:
        buttons.append([{"text": cat.name, "callback": f"category_{cat.id}"}])

    buttons.append([{"text": "◀️ Назад", "callback": "back"}])

    return {"buttons": buttons}


def get_compress_classes_keyboard(classes):
    """Клавиатура с классами компрессии"""
    keyboard = []
    for cls in classes:
        keyboard.append([{"text": cls.name, "callback_data": f"compress_{cls.id}"}])

    keyboard.append([{"text": "◀️ Назад", "callback_data": "back"}])

    return {"inline_keyboard": keyboard}


def get_products_keyboard(products):
    """Клавиатура со списком товаров"""
    buttons = []
    for product in products[:10]:
        text = f"{product.name[:30]} - {product.price} ₽"
        buttons.append([{"text": text, "callback": f"product_{product.id}"}])

    buttons.append([{"text": "⬅️ Назад", "callback": "back"}])

    return {"buttons": buttons}


def get_product_keyboard(product_id):
    """Клавиатура для карточки товара"""
    return {
        "buttons": [
            [
                {"text": "🛒 В корзину", "callback": f"add_to_cart_{product_id}"},
                {"text": "❤️ В избранное", "callback": f"favorite_{product_id}"}
            ],
            [
                {"text": "📏 Таблица размеров", "callback": f"size_table_{product_id}"}
            ],
            [
                {"text": "◀️ Назад к каталогу", "callback": "back_to_catalog"}
            ]
        ]
    }
