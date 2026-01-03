# templatetags/search_tags.py
from django import template
from django.utils.safestring import mark_safe
import re

register = template.Library()


@register.filter
def highlight(text, query):
    """
    Подсвечивает вхождения поискового запроса в тексте.

    Args:
        text: Текст для подсветки
        query: Поисковый запрос для выделения

    Returns:
        Текст с HTML-разметкой подсветки или оригинальный текст при ошибке
    """
    if not text or not query:
        return text

    try:
        # Экранируем специальные символы для regex
        escaped_query = re.escape(str(query))

        # Игнорируем слишком длинные запросы (более 50 символов)
        if len(escaped_query) > 50:
            return text

        # Заменяем все вхождения (без учета регистра)
        pattern = re.compile(escaped_query, re.IGNORECASE)

        # Преобразуем текст в строку
        text_str = str(text)

        # Проверяем, не слишком ли длинный текст (ограничение для производительности)
        if len(text_str) > 10000:
            return text

        highlighted = pattern.sub(
            lambda m: f'<span class="search-highlight">{m.group(0)}</span>',
            text_str
        )
        return mark_safe(highlighted)

    except (re.error, TypeError, ValueError) as e:
        # Логируем ошибку в dev-режиме
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Error in highlight filter: {e}")
        return text

    except Exception as e:
        # Более общий обработчик для непредвиденных ошибок
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Unexpected error in highlight filter: {e}")
        return text


@register.filter
def highlight_words(text, query):
    """
    Более безопасный вариант: подсвечивает отдельные слова из запроса.
    Разбивает запрос на слова и подсвечивает каждое отдельно.
    """
    if not text or not query:
        return text

    try:
        text_str = str(text)
        if len(text_str) > 10000:
            return text

        # Разбиваем запрос на слова
        words = re.findall(r'\w+', str(query))
        if not words:
            return text

        # Для каждого слова создаем pattern
        for word in words[:5]:  # Ограничиваем 5 словами для производительности
            if len(word) < 2:  # Пропускаем слишком короткие слова
                continue

            try:
                pattern = re.compile(re.escape(word), re.IGNORECASE)
                text_str = pattern.sub(
                    lambda m: f'<span class="search-highlight">{m.group(0)}</span>',
                    text_str
                )
            except re.error:
                continue  # Пропускаем проблемные шаблоны

        return mark_safe(text_str)

    except (TypeError, ValueError, AttributeError) as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Error in highlight_words filter: {e}")
        return text


@register.filter
def highlight_phrases(text, query):
    """
    Подсвечивает фразы из запроса, сохраняя порядок слов.
    Более безопасная альтернатива для пользовательского ввода.
    """
    if not text or not query:
        return text

    try:
        text_str = str(text)
        query_str = str(query)

        # Ограничиваем длину для безопасности
        if len(text_str) > 10000 or len(query_str) > 100:
            return text

        # Чистим запрос: удаляем специальные символы кроме пробелов
        clean_query = re.sub(r'[^\w\s]', '', query_str)

        # Берем несколько вариантов запроса
        search_terms = []

        # 1. Весь запрос
        if len(clean_query) >= 2 and len(clean_query) <= 30:
            search_terms.append(clean_query.strip())

        # 2. Отдельные слова (первые 3 слова)
        words = clean_query.split()
        for word in words[:3]:
            if len(word) >= 2:
                search_terms.append(word)

        # 3. Первые 2-3 слова вместе
        if len(words) >= 2:
            search_terms.append(' '.join(words[:2]))

        # Удаляем дубликаты
        search_terms = list(set(search_terms))

        # Применяем подсветку для каждого термина
        for term in search_terms:
            try:
                pattern = re.compile(re.escape(term), re.IGNORECASE)
                text_str = pattern.sub(
                    lambda m: f'<span class="search-highlight">{m.group(0)}</span>',
                    text_str
                )
            except re.error:
                continue

        return mark_safe(text_str)

    except (TypeError, ValueError, AttributeError, MemoryError) as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Error in highlight_phrases filter: {e}")
        return text


# Альтернативная безопасная версия без regex
@register.filter
def highlight_safe(text, query):
    """
    Простая подсветка без использования regex.
    Подходит для ненадежного пользовательского ввода.
    """
    if not text or not query:
        return text

    try:
        text_str = str(text)
        query_str = str(query).lower()

        # Ограничиваем длину для безопасности
        if len(text_str) > 10000 or len(query_str) > 50:
            return text

        # Простой поиск и замена
        highlighted = text_str
        start_index = 0

        while True:
            # Находим вхождение (без учета регистра)
            index = highlighted.lower().find(query_str, start_index)
            if index == -1:
                break

            # Получаем оригинальный текст для замены
            original_text = highlighted[index:index + len(query_str)]

            # Заменяем
            highlighted = (
                highlighted[:index]
                + f'<span class="search-highlight">{original_text}</span>'
                + highlighted[index + len(query_str):]
            )

            # Сдвигаем индекс, чтобы избежать бесконечного цикла
            start_index = index + len(query_str) + len('<span class="search-highlight"></span>')

            # Защита от слишком большого количества замен
            if start_index > len(highlighted) or start_index > 10000:
                break

        return mark_safe(highlighted)

    except (TypeError, ValueError, AttributeError, MemoryError) as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Error in highlight_safe filter: {e}")
        return text
