"""
Клавиатуры для бота MAX
"""


def get_main_keyboard():
    """Главная клавиатура"""
    return [
        [
            {"type": "callback", "text": "🛍 Каталог", "payload": "catalog"},
            {"type": "callback", "text": "❤️ Избранное", "payload": "favorites"},
            {"type": "callback", "text": "🔍 Поиск", "payload": "search"}
        ],
        [
            {"type": "callback", "text": "📦 Корзина", "payload": "cart"},
            {"type": "callback", "text": "📞 Контакты", "payload": "contacts"}
        ],
        [
            {"type": "callback", "text": "❓ Помощь", "payload": "help"}
        ]
    ]


def get_categories_keyboard(categories):
    """Клавиатура с категориями (видами изделий)"""
    buttons = []
    for cat in categories:
        buttons.append([
            {"type": "callback", "text": cat.name, "payload": f"category_{cat.id}"}
        ])
    buttons.append([
        {"type": "callback", "text": "◀️ Назад", "payload": "back"}
    ])
    return buttons


def get_products_keyboard(products):
    """Клавиатура со списком товаров"""
    buttons = []
    for product in products[:10]:
        text = f"{product.name[:30]} - {product.price} ₽"
        buttons.append([
            {"type": "callback", "text": text, "payload": f"product_{product.id}"}
        ])
    buttons.append([
        {"type": "callback", "text": "◀️ Назад", "payload": "back"}
    ])
    return buttons


def get_product_keyboard(product_id):
    """Клавиатура для карточки товара"""
    return [
        [
            {"type": "callback", "text": "🛒 В корзину", "payload": f"add_to_cart_{product_id}"},
            {"type": "callback", "text": "❤️ В избранное", "payload": f"favorite_{product_id}"}
        ],
        [
            {"type": "callback", "text": "📏 Таблица размеров", "payload": f"size_table_{product_id}"}
        ],
        [
            {"type": "callback", "text": "◀️ Назад к каталогу", "payload": "back_to_catalog"}
        ]
    ]


def get_compress_classes_keyboard(classes):
    """Клавиатура с классами компрессии"""
    keyboard = []
    for cls in classes:
        keyboard.append([{"text": cls.name, "callback_data": f"compress_{cls.id}"}])

    keyboard.append([{"text": "◀️ Назад", "callback_data": "back"}])

    return {"inline_keyboard": keyboard}
