from .models import City


# context_processors.py
def city_context(request):
    current_city = None

    # Получаем город из сессии
    if 'current_city_id' in request.session:
        try:
            current_city = City.objects.get(
                id=request.session['current_city_id']
            )
        except (City.DoesNotExist, ValueError):
            # Если город не найден, удаляем из сессии
            if 'current_city_id' in request.session:
                del request.session['current_city_id']
            if 'current_city_name' in request.session:
                del request.session['current_city_name']
    return {
        'current_city': current_city,
        'popular_cities': City.objects.filter(is_popular=True)[:10],
    }
