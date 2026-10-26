# homepage/context.py
from django.db.models import Q


def get_header_context(request):
    """Собирает контекст для шапки: город, популярные города, валюта, погода."""
    from .models import City

    city_id = request.session.get("current_city_id")
    current_city = None

    if city_id:
        try:
            current_city = City.objects.get(id=city_id)
        except City.DoesNotExist:
            pass

    if not current_city:
        try:
            from .services.geo import SimpleGeolocation

            ip = SimpleGeolocation.get_client_ip(request)
            city_name, region_name = SimpleGeolocation.get_city_by_ip(ip)
            if city_name:
                current_city = City.objects.filter(
                    Q(name__iexact=city_name) | Q(region__icontains=region_name)
                ).first()
                if current_city:
                    request.session["current_city_id"] = current_city.id
        except City.DoesNotExist:
            pass

    if not current_city:
        current_city = City.objects.filter(is_default=True).first()
        if current_city:
            request.session["current_city_id"] = current_city.id

    # Валюта и погода — если они у вас считаются где-то ещё,
    # добавьте сюда тот же код, что в get_context_data
    context = {
        "current_city": current_city,
        "popular_cities": City.objects.filter(is_popular=True)[:10],
        # "USD": ..., "EUR": ..., "CNY": ..., "city_temp": ...,
    }
    return context
