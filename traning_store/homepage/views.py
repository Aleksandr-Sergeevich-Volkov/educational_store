from catalog.models import Product
from django.db.models import Count
from django.views.generic import TemplateView


class HomePage(TemplateView):
    # В атрибуте template_name обязательно указывается имя шаблона,
    # на основе которого будет создана возвращаемая страница.
    template_name = 'index.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['prod_count'] = Product.objects.aggregate(Count('id'))
        context['catalog'] = 'catalog/'
        return context
