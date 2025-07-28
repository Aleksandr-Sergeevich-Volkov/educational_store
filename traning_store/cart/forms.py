from catalog.models import Color, Model_type, Size
from django import forms

PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 7)]


class CartAddProductForm(forms.Form):
    quantity = forms.TypedChoiceField(label='Кол-во', choices=PRODUCT_QUANTITY_CHOICES,
                                      coerce=int)
    update = forms.BooleanField(required=False, initial=False,
                                widget=forms.HiddenInput)
    size = forms.ModelChoiceField(label='Размер',
                                  queryset=Size.objects.all(), required=False)
    color = forms.ModelChoiceField(label='Цвет',
                                   queryset=Color.objects.all(),
                                   required=False)
    m_type = forms.ModelChoiceField(label='Тип',
                                    queryset=Model_type.objects.all(),
                                    required=False)


class DeliveryForm(forms.Form):
    pvz_id = forms.CharField(label='Пункт выдачи',
                             max_length=200, required=False)
    address_pvz = forms.CharField(label='Адрес',
                                  max_length=200, required=False)
