from django import forms
from catalog.models import Color, Size, Model_type

PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 7)]


class CartAddProductForm(forms.Form):
    quantity = forms.TypedChoiceField(choices=PRODUCT_QUANTITY_CHOICES, coerce=int)
    update = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)
    size = forms.ModelChoiceField(label='Размер', queryset=Size.objects.all(), required=False)
    color = forms.ModelChoiceField(label='Цвет', queryset=Color.objects.all(), required=False)
    m_type = forms.ModelChoiceField(label='Тип', queryset=Model_type.objects.all(), required=False)

