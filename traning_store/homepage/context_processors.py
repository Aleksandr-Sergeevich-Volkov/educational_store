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
        except City.DoesNotExist:
            pass
        return {
            'current_city': current_city,
            'popular_cities': City.objects.filter(is_popular=True)[:10],
        }
