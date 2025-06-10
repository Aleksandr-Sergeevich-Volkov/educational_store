import decimal
import hashlib
from urllib import parse
from urllib.parse import urlparse

from catalog.forms import SignUpForm
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import is_valid_path, reverse_lazy
from django.views.generic.edit import CreateView
from orders.models import Order

from .settings import ROBOKASSA_PASSWORD_U1, ROBOKASSA_PASSWORD_U2


class SomeEntityCreateView(CreateView):
    template_name = 'registration/registration_form.html'
    form_class = SignUpForm
    success_url = reverse_lazy('homepage:homepage')


def login_view(request):
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
    return f'{robokassa_payment_url}?{parse.urlencode(data).replace("%40","@")}'


# Получение уведомления об исполнении операции (ResultURL).

def result_payment(request: str, merchant_password_2: str) -> str:
    """Verification of notification (ResultURL).
    :param request: HTTP parameters.
    """
    merchant_password_2 = ROBOKASSA_PASSWORD_U2
    param_request = parse_response(request)
    cost = param_request['OutSum']
    number = param_request['InvId']
    signature = param_request['SignatureValue']
    if check_signature_result(number, cost, signature, merchant_password_2):
        return HttpResponse(f'OK{param_request["InvId"]}')
    return HttpResponse('bad sign')


# Проверка параметров в скрипте завершения операции (SuccessURL).

def check_success_payment(request: str, merchant_password_1: str = ROBOKASSA_PASSWORD_U1) -> str:
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
