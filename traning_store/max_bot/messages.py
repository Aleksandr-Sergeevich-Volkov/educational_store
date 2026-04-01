"""
Форматирование сообщений для бота MAX
"""


def format_product_card(product):
    """Форматирует карточку товара"""
    text = f"""
📦 *{product.name}*

💰 *Цена:* {product.price:,.0f} ₽
📦 *Наличие:* {'В наличии' if product.stock > 0 else 'Под заказ'}
🏷 *Артикул:* {product.articul}
🏭 *Бренд:* {product.brand.name}
📊 *Класс компрессии:* {product.Class_compress.name}
👤 *Пол:* {product.Male.name if product.Male else 'Унисекс'}
"""
    if product.Color.exists():
        colors = ', '.join([c.name for c in product.Color.all()])
        text += f"🎨 *Цвета:* {colors}\n"
    if product.Type_product:
        text += f"🧦 *Вид:* {product.Type_product.name}\n"
    if product.seo_description:
        text += f"\n📝 *Описание:*\n{product.seo_description[:200]}...\n"
    return text


def format_product_list(products, title="🛍 Наши товары"):
    """Форматирует список товаров"""
    if not products.exists():
        return "😔 Товары не найдены"

    text = f"{title}\n\n"
    for p in products[:10]:
        text += f"• *{p.name[:40]}*\n"
        text += f"  💰 {p.price:,.0f} ₽ | 📦 {'В наличии' if p.stock > 0 else 'Под заказ'}\n"
        text += f"  🆔 {p.articul}\n\n"

    if products.count() > 10:
        text += f"\n📊 Всего товаров: {products.count()}. Показаны первые 10."

    return text


def get_start_message():
    """Приветственное сообщение"""
    return """
👋 *Добро пожаловать в магазин компрессионного трикотажа!*

Мы предлагаем качественный лечебный трикотаж от ведущих производителей:
• ORTO
• Luomia Idealista
• Ergoforma
• Trives
• И другие

🛍 *Что вы можете сделать:*
• Просмотреть каталог
• Подобрать товар по классу компрессии
• Получить консультацию по размерам
• Оформить заказ с доставкой

📌 *Начните с кнопки «Каталог» ниже*
"""


def get_help_message():
    """Помощь"""
    return """
❓ *Помощь*

Доступные команды:
/catalog - открыть каталог
/search - поиск товаров
/cart - корзина
/help - эта справка

📞 *Контакты поддержки:*
Телефон: +7 (906) 717-48-77
Email: info@kompressionnye-chulki24.ru

⏰ Режим работы: Пн-Пт 9:00-18:00
"""


def get_cart_message(cart_items):
    """Сообщение с корзиной (заглушка)"""
    return "🛒 Функция корзины в разработке. Скоро появится!"
