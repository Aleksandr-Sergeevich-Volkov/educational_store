from django.views.generic import TemplateView
from catalog.models import Product
from django.db.models import Count


class HomePage(TemplateView):
    # В атрибуте template_name обязательно указывается имя шаблона,
    # на основе которого будет создана возвращаемая страница.
    template_name = 'index.html' 
    def get_context_data(self, *args, **kwargs):
<<<<<<< HEAD
        context = super().get_context_data(*args, **kwargs)
        context['prod_count'] = Product.objects.aggregate(Count('id')) 
=======
        context = super(HomePage.self).get_context_data(*args, **kwargs)
>>>>>>> 0295487ebcd6703410438ae8a892e0c32d23850d
        context['catalog'] = 'catalog/'
        return context
     
