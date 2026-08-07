import logging

from django import forms
from django.db import models

from .models import Order

logger = logging.getLogger(__name__)


class OrderCreateForm(forms.ModelForm):
    first_name = models.CharField("Имя", max_length=20)
    last_name = models.CharField("Фамилия", max_length=20)
    email = models.EmailField("Почта", max_length=300)
    address = models.CharField("Адрес", max_length=20)
    delivery_type = models.CharField("Доставка", max_length=20)
    address_pvz = models.CharField("Адрес ПВЗ", max_length=20)
    postal_code = models.CharField("Индекс", max_length=20)
    city = models.CharField("Город", max_length=20)

    class Meta:
        model = Order
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "address",
            "address_pvz",
            "delivery_type",
            "postal_code",
            "city",
        ]
        labels = {
            "first_name": "Имя",
            "last_name": "Фамилия",
            "email": "Почта",
            "phone": "Телефон для доставки",
            "address": "Адрес",
            "delivery_type": "Доставка",
            "address_pvz": "Адрес ПВЗ",
            "postal_code": "Индекс",
            "city": "Город",
        }

    def __init__(self, *args, **kwargs):
        super(OrderCreateForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({"class": "form-control"})

    widgets = {
        "phone": forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "+7 (XXX) XXX-XX-XX",
                "type": "tel",
                "pattern": r"^\+7\d{10}$",
                "maxlength": "20",
            }
        )
    }

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if phone:
            # Удаляем пробелы и символы форматирования
            cleaned = "".join(filter(str.isdigit, phone))

            # Если номер начинается с 8, заменяем на +7
            if cleaned.startswith("8"):
                cleaned = "7" + cleaned[1:]

            # Добавляем +7 если нет
            if not cleaned.startswith("7"):
                cleaned = "7" + cleaned

            # Возвращаем в формате +7XXXXXXXXXX
            result = "+" + cleaned
            if len(result) != 12:
                raise forms.ValidationError("Номер должен содержать 10 цифр")
            return result
        return phone


class OrderCreateFormСourier(forms.ModelForm):
    first_name = models.CharField("Имя", max_length=20)
    last_name = models.CharField("Фамилия", max_length=20)
    email = models.EmailField("Почта", max_length=300)
    address = models.CharField("Адрес", max_length=20)
    postal_code = models.CharField("Индекс", max_length=20)
    city = models.CharField("Город", max_length=20)

    class Meta:
        model = Order
        fields = ["first_name", "last_name", "email", "address", "postal_code", "city"]
        labels = {
            "first_name": "Имя",
            "last_name": "Фамилия",
            "email": "Почта",
            "address": "Адрес",
            "postal_code": "Индекс",
            "city": "Город",
        }

    def __init__(self, *args, **kwargs):
        super(OrderCreateFormСourier, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({"class": "form-control"})
