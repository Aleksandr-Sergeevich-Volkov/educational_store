import decimal
import hashlib
from urllib import parse
from urllib.parse import urlparse

from catalog.forms import SignUpForm
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from orders.models import Order

from .settings import ROBOKASSA_PASSWORD_1, ROBOKASSA_PASSWORD_2


class SomeEntityCreateView(CreateView):
    template_name = 'registration/registration_form.html'
    form_class = SignUpForm
    success_url = reverse_lazy('homepage:homepage')


""" def login_view(request):
    next_url = request.META.get('HTTP_REFERER')

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Ensure next_url is safe or default to home page
            next_url = request.POST.get('next', next_url)
            parsed_url = urlparse(next_url)
            if not parsed_url.netloc and is_valid_path(next_url):
                return HttpResponseRedirect(next_url)
            return HttpResponseRedirect(next_url)
    else:
        form = AuthenticationForm()

    return render(request, 'registration/login.html', {'form': form, 'next': next_url})
 """


def login_view(request):
    # Получаем next из GET параметров или из POST
    next_url = request.GET.get('next') or request.POST.get('next')

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Проверяем next URL
            next_url = request.POST.get('next', '')

            # Безопасная проверка URL
            if next_url and next_url != 'None':
                # Убедимся, что next_url не содержит 'None'
                if 'None' not in next_url:
                    # Проверяем, что URL принадлежит нашему домену
                    from urllib.parse import urlparse
                    parsed = urlparse(next_url)

                    # Разрешаем редирект если:
                    # 1. Нет домена (относительный URL) ИЛИ
                    # 2. Домен совпадает с нашим
                    if not parsed.netloc or parsed.netloc == request.get_host():
                        return HttpResponseRedirect(next_url)

            # По умолчанию редирект на главную
            return redirect('home')
    else:
        form = AuthenticationForm()

    # Очищаем next_url если он 'None'
    if next_url == 'None':
        next_url = ''

    return render(request, 'registration/login.html', {
        'form': form,
        'next': next_url or ''
    })


def logout_view(request):
    logout(request)
    return redirect('/')


def calculate_signature(*args) -> str:
    """Create signature MD5.
    """
    return hashlib.md5(':'.join(str(arg) for arg in args).encode()).hexdigest()


def parse_response(request: str) -> dict:
    """
    :param request: Link.
    :return: Dictionary.
    """
    url = request.META.get('RAW_URI')
    params = {}
    for item in urlparse(url).query.split('&'):
        key, value = item.split('=')
        params[key] = value
    return params


def check_signature_result(
    order_number: int,  # invoice number
    received_sum: decimal,  # cost of goods, RU
    received_signature: hex,  # SignatureValue
    password: str  # Merchant password
) -> bool:
    signature = calculate_signature(received_sum, order_number, password)
    if signature.lower() == received_signature.lower():
        return True
    return False


# Формирование URL переадресации пользователя на оплату.

def generate_payment_link(
    merchant_login: str,  # Merchant login
    merchant_password_1: str,  # Merchant password
    cost: decimal,  # Cost of goods, RU
    number: int,  # Invoice number
    description: str,  # Description of the purchase
    is_test=0,
    robokassa_payment_url='https://auth.robokassa.ru/Merchant/Index.aspx',
    email='test@mail.ru',
) -> str:
    """URL for redirection of the customer to the service."""

    signature = calculate_signature(
        merchant_login,
        cost,
        number,
        merchant_password_1
    )

    data = {
        'MerchantLogin': merchant_login,
        'OutSum': cost,
        'InvId': number,
        'Description': description,
        'SignatureValue': signature,
        'IsTest': is_test,
        'Email': email
    }
    return f'{robokassa_payment_url}?{parse.urlencode(data)}'


# Получение уведомления об исполнении операции (ResultURL).

def result_payment(request: str, merchant_password_2: str) -> str:
    """Verification of notification (ResultURL).
    :param request: HTTP parameters.
    """
    merchant_password_2 = ROBOKASSA_PASSWORD_2
    param_request = parse_response(request)
    cost = param_request['OutSum']
    number = param_request['InvId']
    signature = param_request['SignatureValue']
    if check_signature_result(number, cost, signature, merchant_password_2):
        return HttpResponse(f'OK{param_request["InvId"]}')
    return HttpResponse('bad sign')


# Проверка параметров в скрипте завершения операции (SuccessURL).

def check_success_payment(request: str, merchant_password_1: str = ROBOKASSA_PASSWORD_1) -> str:
    """ Verification of operation parameters ("cashier check") in SuccessURL script.
    :param request: HTTP parameters"""
    param_request = parse_response(request)
    cost = param_request['OutSum']
    number = param_request['InvId']
    signature = param_request['SignatureValue']
    if check_signature_result(number, cost, signature, merchant_password_1):
        order = Order.objects.get(pk=param_request['InvId'])
        order.paid = True
        order.save()
        return HttpResponse('Thank you for using our service')
    return HttpResponse('bad sign')


def staff_required(function=None):
    """
    Декоратор для проверки, что пользователь является staff
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_staff,
        login_url='/admin-login/'
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def admin_login(request):
    """
    Кастомная страница входа ТОЛЬКО для админки
    """
    # Если пользователь уже авторизован и является staff, перенаправляем в админку
    if request.user.is_authenticated and request.user.is_staff:
        return redirect(settings.ADMIN_URL)

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_staff:  # Проверяем, что пользователь является staff
                login(request, user)
                messages.success(request, f'Добро пожаловать в админку, {username}!')
                next_page = request.GET.get('next', settings.ADMIN_URL)
                return redirect(next_page)
            else:
                messages.error(request, 'У вас нет доступа к админке')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')

    return render(request, 'registration/admin_login.html')


def home(request):
    return render(request, 'home.html')
