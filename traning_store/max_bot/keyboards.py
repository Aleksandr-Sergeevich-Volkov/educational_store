"""
Клавиатуры для бота MAX
"""


def get_main_keyboard():
    """Главная клавиатура"""
    return [
        [
            {"type": "callback", "text": "🛍 Каталог", "payload": "catalog"},
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
    """Клавиатура с категориями"""
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
