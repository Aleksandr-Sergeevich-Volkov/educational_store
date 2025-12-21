import random

from catalog.models import Gallery, Product, SizeDetail
from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import SearchQuery, SearchVector
from django.db import models
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.template.defaulttags import register
from django.urls import reverse
from django.views.generic import TemplateView

from .forms import (CommentForm, SearchForm, SizeFinderForm,
                    SmartMeasurementForm)
from .models import Comment, Post


class HomePage(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['text'] = Post.objects.all().annotate(comment_count=models.Count('comments')).order_by('id')
        context['prod_count'] = Product.objects.aggregate(Count('id'))
        product_list = [x for x in range(context['prod_count']['id__count'])]
        random_list = random.shuffle(product_list)
        context['random_list'] = random_list
        context['product'] = Product.objects.filter(id__in=product_list[:3])
        return context


def search(request):
    form = SearchForm(request.GET)
    results = None
    query = ''
    if form.is_valid():
        query = form.cleaned_data['query']
        if query:
            results = Product.objects.annotate(search=SearchVector(
                'name', 'Type_product', 'brand')).filter(
                search=SearchQuery(query)).prefetch_related(
                models.Prefetch(
                    'images',
                    queryset=Gallery.objects.filter(main=True),
                    to_attr='main_images'))
    else:
        results = Product.objects.none()
    return render(request, 'search.html', {'form': form, 'results': results, 'query': query})


def detail_view(request, pk):
    object = get_object_or_404(Post, pk=pk)
    form = CommentForm()
    comments = object.comments.all().order_by('created_at')
    return render(request, 'detail.html', {'object' : object,
                                           'form' : form,
                                           'comments' : comments})


@login_required
def add_comment(request, post_id):
    print(f'test{post_id}')
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    # return redirect('homepage:detail', pk=post_id)
    # Возвращаем на главную с параметром, какой блок открыть
    return redirect(f'{reverse("homepage:homepage")}?open_comments={post_id}')


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    post = get_object_or_404(Post, pk=comment.post_id)
    if comment.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)
    form = CommentForm(request.POST or None, instance=comment)
    context = {'form': form,
               'comment': comment,
               'post': post,
               }
    if request.method == 'POST':
        form = CommentForm(request.POST,
                           instance=comment,
                           )
        if form.is_valid():
            form.save()
        return redirect(f'{reverse("homepage:homepage")}?open_comments={post_id}')
        # return redirect('homepage:detail', pk=post_id)
    return render(request, 'blog/comment.html', context)


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if comment.author != request.user:
        return redirect('homepage:detail', pk=post_id)
    context = {'comment': comment, }
    if request.method == 'POST':
        comment.delete()
        return redirect(f'{reverse("homepage:homepage")}?open_comments={post_id}')
        # return redirect('homepage:detail', pk=post_id)
    return render(request, 'blog/comment.html', context)


@register.filter
def get_attribute(obj, attr_name):
    """Шаблонный фильтр для получения атрибута по имени"""
    return getattr(obj, attr_name, None)


def get_measurement_fields_config(brand):
    """Возвращает конфигурацию полей для отображения в результатах"""
    # Получаем пример размера для бренда
    sample_size = SizeDetail.objects.filter(size__brand=brand).first()
    if not sample_size:
        return {}

    fields_config = {
        'ankle_circumference': {
            'verbose_name': 'Обхват щиколотки',
            'show_in_results': True
        },
        'calf_circumference': {
            'verbose_name': 'Обхват икры',
            'show_in_results': True
        },
        'mid_thigh_circumference': {
            'verbose_name': 'Обхват середины бедра',
            'show_in_results': bool(getattr(sample_size, 'mid_thigh_circumference', None))
        },
        'circumference_under_knee': {
            'verbose_name': 'Обхват под коленом',
            'show_in_results': bool(getattr(sample_size, 'circumference_under_knee', None))
        },
        'Upper_thigh_circumference': {
            'verbose_name': 'Обхват бедра верхний',
            'show_in_results': bool(getattr(sample_size, 'Upper_thigh_circumference', None))
        }
    }

    return fields_config


def size_finder(request):
    brand_form = SizeFinderForm(request.POST or None)
    measurement_form = None
    results = []
    selected_brand = None
    measurement_fields = {}  # Инициализируем пустым словарем

    if request.method == 'POST':
        if brand_form.is_valid():
            selected_brand = brand_form.cleaned_data['brand']

            # Используем динамическую форму
            measurement_form = SmartMeasurementForm(
                request.POST,
                brand=selected_brand
            )

            if measurement_form and measurement_form.is_valid():
                measurements = measurement_form.cleaned_data
                results = find_matching_sizes(selected_brand, measurements)

                # Определяем какие поля показывать в результатах
                measurement_fields = get_measurement_fields_config(selected_brand)

    return render(request, 'size_finder.html', {
        'brand_form': brand_form,
        'measurement_form': measurement_form,
        'results': results,
        'selected_brand': selected_brand,
        'measurement_fields': measurement_fields,
    })


def find_matching_sizes(brand, measurements):
    """Находит подходящие размеры по измерениям"""
    suitable_sizes = []
    size_details = SizeDetail.objects.filter(size__brand=brand)

    for size_detail in size_details:
        if is_size_match(size_detail, measurements):
            suitable_sizes.append(size_detail)

    return suitable_sizes


def is_size_match(size_detail, measurements):
    """Проверяет, подходит ли размер по ВСЕМ введенным измерениям"""
    for field_name, user_value in measurements.items():
        if not size_detail.is_measurement_in_range(field_name, user_value):
            return False
    return True
