from django.views.generic import TemplateView


class HomePage(TemplateView):
    # В атрибуте template_name обязательно указывается имя шаблона,
    # на основе которого будет создана возвращаемая страница.
    template_name = 'index.html' 
    def get_context_data(self, *args, **kwargs):
        context = super(HomePage.self).get_context_data(*args, **kwargs)
        context['catalog'] = 'catalog/'
        return context
     
