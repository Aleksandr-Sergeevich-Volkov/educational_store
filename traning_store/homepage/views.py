from catalog.models import Product
from django.db.models import Count
from django.shortcuts import get_object_or_404, render
from django.views.generic import TemplateView

from .models import Post


class HomePage(TemplateView):
    # В атрибуте template_name обязательно указывается имя шаблона,
    # на основе которого будет создана возвращаемая страница.
    template_name = 'index.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['text'] = Post.objects.all()
        context['prod_count'] = Product.objects.aggregate(Count('id'))
        context['catalog'] = 'catalog/'
        return context


def detail_view(request, pk):
    object = get_object_or_404(Post, pk=pk)
    return render(request, 'detail.html', {'object': object})
