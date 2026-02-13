import logging

from catalog.models import (Appointment, Brend, Class_compress, Color, Gallery,
                            Male, Model_type, Product, Side, Size, SizeDetail,
                            Soсk, Type_product, Wide_hips)
from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import TrigramSimilarity
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.db.models import Count, Prefetch, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.defaulttags import register
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST
from django.views.generic import TemplateView

from .core.mixins import CityContextMixin
from .forms import (CommentForm, SearchForm, SizeFinderForm,
                    SmartMeasurementForm)
from .models import City, Comment, Post

logger = logging.getLogger(__name__)


class HomePage(CityContextMixin, TemplateView):
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        """
        Обрабатывает GET запрос, включая смену города
        """
        # Проверяем параметры смены города
        city_id = request.GET.get('city_id')
        change_city = request.GET.get('change_city')

        if city_id and change_city:
            try:
                from .models import City
                city = City.objects.get(id=city_id)
                # Сохраняем в сессии
                request.session['current_city_id'] = city.id
                request.session.modified = True
                # УВЕЛИЧИВАЕМ СЧЕТЧИК ПРИ РУЧНОЙ СМЕНЕ ГОРОДА
                self.increment_city_detection_count(city)

                # Редирект на ту же страницу без параметров
                from django.shortcuts import redirect
                return redirect('homepage:homepage')

            except City.DoesNotExist:
                pass  # Город не найден, продолжаем как обычно

        # Если не было смены города, вызываем стандартный обработчик
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        # Ваш существующий код получения города...
        from .models import City

        city_id = self.request.session.get('current_city_id')
        current_city = None

        if city_id:
            try:
                current_city = City.objects.get(id=city_id)
            except City.DoesNotExist:
                pass

        if not current_city:
            try:
                from .services.geo import SimpleGeolocation
                ip = SimpleGeolocation.get_client_ip(self.request)
                city_name, region_name = SimpleGeolocation.get_city_by_ip(ip)

                if city_name:
                    from django.db.models import Q
                    current_city = City.objects.filter(
                        Q(name__iexact=city_name)
                        | Q(region__icontains=region_name)
                    ).first()

                    if current_city:
                        self.request.session['current_city_id'] = current_city.id
            except City.DoesNotExist:
                pass

        if not current_city:
            current_city = City.objects.filter(is_default=True).first()
            if current_city:
                self.request.session['current_city_id'] = current_city.id

        context['current_city'] = current_city
        context['popular_cities'] = City.objects.filter(is_popular=True)[:10]

        # 3. Остальной ваш код...
        context['search_form'] = SearchForm()

        context['text'] = Post.objects.all().annotate(
            comment_count=models.Count('comments')
        ).order_by('id')

        context['prod_count'] = Product.objects.aggregate(Count('id'))

        if Product.objects.exists():
            context['popular_products'] = Product.objects.order_by('-views')[:5].prefetch_related(
                models.Prefetch('images',
                                queryset=Gallery.objects.filter(main=True),
                                to_attr='main_images'))
        else:
            context['popular_products'] = Product.objects.none()

        from catalog.models import Brend, Type_product
        context['popular_categories'] = Type_product.objects.all()[:4]
        context['popular_brands'] = Brend.objects.all()[:6]
        return context


def search(request):
    form = SearchForm(request.GET)
    query = ''
    results = None
    filters = {}

    if form.is_valid():
        query = form.cleaned_data['query']
        # Базовый запрос с предзагрузкой
        base_query = Product.objects.select_related(
            'brand', 'Appointment', 'Male', 'Class_compress',
            'Sock', 'Type_product', 'Size', 'Model_type',
            'Wide_hips', 'Side'
        ).prefetch_related(
            'Color',
            Prefetch(
                'images',
                queryset=Gallery.objects.filter(main=True),
                to_attr='main_images'
            )
        )
        if query:
            # Используем триграммы для нечеткого поиска
            products = base_query.annotate(
                similarity=TrigramSimilarity('name', query) + TrigramSimilarity('articul', query) * 0.8 + TrigramSimilarity('brand__name', query) * 0.7
            ).filter(
                Q(similarity__gt=0.1)
                | Q(name__icontains=query)
                | Q(articul__icontains=query)
                | Q(code__icontains=query)
                | Q(brand__name__icontains=query)
                | Q(Type_product__name__icontains=query)
                | Q(Appointment__name__icontains=query)
            ).order_by('-similarity')
        else:
            products = base_query.all()

        # Динамические фильтры из GET параметров
        filter_mapping = {
            'brand': 'brand__id__in',
            'appointment': 'Appointment__id__in',
            'male': 'Male__id__in',
            'color': 'Color__id__in',
            'class_compress': 'Class_compress__id__in',
            'sock': 'Sock__id__in',
            'type_product': 'Type_product__id__in',
            'size': 'Size__id__in',
            'model_type': 'Model_type__id__in',
            'wide_hips': 'Wide_hips__id__in',
            'side': 'Side__id__in',
            'price_min': 'price__gte',
            'price_max': 'price__lte',
        }

        for param, filter_field in filter_mapping.items():
            value = request.GET.get(param)
            if value:
                if param in ['price_min', 'price_max']:
                    products = products.filter(**{filter_field: value})
                else:
                    # Для множественного выбора (через запятую)
                    ids = [int(x) for x in value.split(',') if x.isdigit()]
                    if ids:
                        products = products.filter(**{filter_field: ids})
                        filters[param] = ids

        # Сортировка
        sort_options = {
            'price_asc': 'price',
            'price_desc': '-price',
            'name_asc': 'name',
            'name_desc': '-name',
            'popular': '-code',  # или другое поле для популярности
            'new': '-id',
        }
        sort_by = request.GET.get('sort', 'new')
        products = products.order_by(sort_options.get(sort_by, '-id'))
        # Пагинация
        paginator = Paginator(products, 6)  # 6 товара на страницу

        page_number = request.GET.get('page')
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        prod_count = paginator.count

    # Получаем доступные значения для фильтров
    filter_context = {
        'brands': Brend.objects.all(),
        'appointments': Appointment.objects.all(),
        'males': Male.objects.all(),
        'colors': Color.objects.all(),
        'class_compresses': Class_compress.objects.all(),
        'socks': Soсk.objects.all(),
        'type_products': Type_product.objects.all(),
        'sizes': Size.objects.all(),
        'model_types': Model_type.objects.all(),
        'wide_hips_list': Wide_hips.objects.all(),
        'sides': Side.objects.all(),
    }

    return render(request, 'search.html', {
        'form': form,
        'results': results,
        'query': query,
        'page_obj': page_obj,
        'prod_count': prod_count,
        'filters': filters,
        'per_page': int(request.GET.get('per_page', 24)),
        **filter_context
    })


@require_GET
def autocomplete(request):
    """
    AJAX-функция для автодополнения.
    Возвращает JSON с подсказками, не HTML страницу.
    """
    term = request.GET.get('term', '').strip()
    # Если меньше 2 символов - не ищем
    if len(term) < 2:
        return JsonResponse({'suggestions': []})

    try:
        # Упрощенный поиск для автодополнения (быстрый)
        products = Product.objects.filter(
            Q(name__icontains=term)
            | Q(articul__icontains=term)
        ).select_related('brand').prefetch_related(
            models.Prefetch(
                'images',
                queryset=Gallery.objects.filter(main=True),
                to_attr='main_images'
            ))[:10]  # Только 10 результатов для скорости
        suggestions = []
        for product in products:
            main_image = ''
            if hasattr(product, 'main_images') and product.main_images:
                main_image = product.main_images[0].image.url
            suggestions.append({
                'id': product.id,
                'name': product.name,
                'brand': product.brand.name,
                'articul': product.articul,
                'price': str(product.price),
                'url': product.get_absolute_url(),
                'image': main_image,
            })
        return JsonResponse({'suggestions': suggestions})
    except Exception as e:
        # В случае ошибки возвращаем пустой список
        return JsonResponse({'suggestions': [], 'error': str(e)})


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


@require_POST
def detect_city(request):
    """Определение города по IP"""
    try:
        from django.db.models import Q

        from .models import City
        from .services.geo import SimpleGeolocation

        ip = SimpleGeolocation.get_client_ip(request)
        print(f"Определение города для IP: {ip}")  # Для логов

        city_name, region_name = SimpleGeolocation.get_city_by_ip(ip)

        if city_name:
            # Ищем город в базе
            city = City.objects.filter(
                Q(name__iexact=city_name)
                | Q(region__icontains=region_name)
            ).first()

            if city:
                request.session['current_city_id'] = city.id
                return JsonResponse({
                    'success': True,
                    'city': city.name,
                    'message': f'Город определен: {city.name}'
                })
            else:
                # Город найден API, но нет в нашей базе
                return JsonResponse({
                    'success': False,
                    'message': f'Город {city_name} не найден в нашей базе'
                })
        else:
            # API не смог определить город
            return JsonResponse({
                'success': False,
                'message': 'Не удалось определить город по IP'
            })

    except Exception as e:
        print(f"Ошибка при определении города: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Ошибка сервера: {str(e)}'
        })


def search_city(request):
    """Поиск городов по названию"""
    query = request.GET.get('q', '')
    cities = []

    if len(query) >= 2:
        cities = City.objects.filter(
            Q(name__icontains=query)
            | Q(region__icontains=query)
        ).values('id', 'name', 'region')[:20]

    return JsonResponse(list(cities), safe=False)

# views.py в вашем основном приложении


def handler404(request, exception):
    logger.debug(f"handler404 вызван для пути: {request.path}")
    logger.debug(f"Исключение: {exception}")
    # Кастомный обработчик 404 ошибки.
    # Получаем популярные товары для отображения на странице 404

    context = {
        'title': '404 - Страница не найдена',
        'message': 'Извините, такой страницы не существует.',
        'request_path': request.path,
    }
    return render(request, '404.html', context, status=404)


def handler500(request):
    """Кастомный обработчик 500 ошибки."""
    return render(request, '500.html', status=500)


def handler403(request, exception):
    """Кастомный обработчик 403 ошибки."""
    return render(request, '403.html', status=403)
