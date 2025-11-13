import random

from catalog.models import Gallery, Product, SizeDetail
from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import SearchQuery, SearchVector
from django.db import models
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import TemplateView

from .forms import (CommentForm, ORTOMeasurementForm, SearchForm,
                    SizeFinderForm, TrivesMeasurementForm,
                    VenoteksMeasurementForm)
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
    return redirect('homepage:detail', pk=post_id)


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
        return redirect('homepage:detail', pk=post_id)
    return render(request, 'blog/comment.html', context)


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if comment.author != request.user:
        return redirect('homepage:detail', pk=post_id)
    context = {'comment': comment, }
    if request.method == 'POST':
        comment.delete()
        return redirect('homepage:detail', pk=post_id)
    return render(request, 'blog/comment.html', context)


def size_finder(request):
    brand_form = SizeFinderForm(request.POST or None)
    measurement_form = None
    results = []
    selected_brand = None

    if request.method == 'POST':
        if brand_form.is_valid():
            selected_brand = brand_form.cleaned_data['brand']

            # Определяем какая форма измерений нужна по названию бренда
            brand_name = selected_brand.name.lower()

            if 'venoteks' in brand_name:
                measurement_form = VenoteksMeasurementForm(request.POST)
            elif 'orto' in brand_name:
                measurement_form = ORTOMeasurementForm(request.POST)
            elif 'trives' in brand_name:
                measurement_form = TrivesMeasurementForm(request.POST)
            else:
                # Форма по умолчанию, если бренд не распознан
                measurement_form = VenoteksMeasurementForm(request.POST)

            if measurement_form and measurement_form.is_valid():
                measurements = measurement_form.cleaned_data
                results = find_matching_sizes(selected_brand, measurements, brand_name)

    return render(request, 'size_finder.html', {
        'brand_form': brand_form,
        'measurement_form': measurement_form,
        'results': results,
        'selected_brand': selected_brand,
    })


def find_matching_sizes(brand, measurements, brand_name):
    """Находит подходящие размеры по измерениям"""
    suitable_sizes = []

    # Получаем все размеры для выбранного бренда
    size_details = SizeDetail.objects.filter(size__brand=brand)

    for size_detail in size_details:
        if is_size_match(size_detail, brand_name, measurements):
            suitable_sizes.append(size_detail)

    return suitable_sizes


def is_size_match(size_detail, brand_name, measurements):
    """Проверяет, подходит ли размер по всем измерениям"""
    if 'venoteks' in brand_name:
        return (
            size_detail.is_measurement_in_range('ankle_circumference', measurements['ankle_circumference'])
            and size_detail.is_measurement_in_range('calf_circumference', measurements['calf_circumference'])
            and size_detail.is_measurement_in_range('mid_thigh_circumference', measurements['mid_thigh_circumference'])
        )
    elif 'orto' in brand_name:
        return (
            size_detail.is_measurement_in_range('ankle_circumference', measurements['ankle_circumference'])
            and size_detail.is_measurement_in_range('calf_circumference', measurements['calf_circumference'])
            and size_detail.is_measurement_in_range('circumference_under_knee', measurements['circumference_under_knee'])
            and size_detail.is_measurement_in_range('mid_thigh_circumference', measurements['mid_thigh_circumference'])
            and size_detail.is_measurement_in_range('Upper_thigh_circumference', measurements['upper_thigh_circumference'])
        )
    elif 'trives' in brand_name:
        return (
            size_detail.is_measurement_in_range('ankle_circumference', measurements['ankle_circumference'])
            and size_detail.is_measurement_in_range('calf_circumference', measurements['calf_circumference'])
            and size_detail.is_measurement_in_range('circumference_under_knee', measurements['circumference_under_knee'])
            and size_detail.is_measurement_in_range('Upper_thigh_circumference', measurements['upper_thigh_circumference'])
        )
    return False
