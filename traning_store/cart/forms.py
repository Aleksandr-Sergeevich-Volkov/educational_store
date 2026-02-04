from catalog.models import Color, Model_type, Size
from django import forms

PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 7)]


class CartAddProductForm(forms.Form):
    quantity = forms.TypedChoiceField(
        label='Кол-во',
        choices=PRODUCT_QUANTITY_CHOICES,
        coerce=int,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    update = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.HiddenInput
    )
    size = forms.ModelChoiceField(
        label='Размер',
        queryset=Size.objects.none(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    color = forms.ModelChoiceField(
        label='Цвет',
        queryset=Color.objects.none(),
        required=True,
        error_messages={
            'required': 'Пожалуйста, выберите цвет'
        },
        widget=forms.RadioSelect(attrs={'class': 'color-radio'})
    )
    m_type = forms.ModelChoiceField(
        label='Тип',
        queryset=Model_type.objects.none(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        product = kwargs.pop('product', None)
        super().__init__(*args, **kwargs)

        if product:
            available_colors = product.Color.all()

            if available_colors.exists():
                # ВАЖНО: Используем prefetch_related или select_related если нужно
                self.fields['color'].queryset = available_colors
                if available_colors.count() == 1:
                    single_color = available_colors.first()
                    self.fields['color'].initial = single_color
                    self.fields['color'].widget = forms.HiddenInput()
                    # Добавляем скрытое поле с id цвета
                    self.fields['color_hidden'] = forms.CharField(
                        initial=single_color.id,
                        widget=forms.HiddenInput()
                    )
                else:
                    self.fields['color'].queryset = available_colors
                    self.fields['color'].empty_label = None
            else:
                # Если цветов нет, скрываем поле и добавляем ошибку
                self.fields['color'].widget = forms.HiddenInput()
                self.fields['color'].required = False
                self.add_error(None, "Для этого товара не указаны доступные цвета")

        if product and product.brand:
            self.fields['m_type'].queryset = Model_type.objects.filter(
                brand=product.brand
            )
            self.fields['size'].queryset = Size.objects.filter(
                brand=product.brand
            )

    # ДОБАВЬТЕ ЭТОТ МЕТОД ДЛЯ ЗАГРУЗКИ ОБЪЕКТОВ
    def get_color_choices(self):
        """Возвращает цвета с полными объектами"""

    def clean_color(self):
        color = self.cleaned_data.get('color')
        if not color:
            raise forms.ValidationError("Пожалуйста, выберите цвет")
        return color

    def clean(self):
        cleaned_data = super().clean()
        color = cleaned_data.get('color')

        if not color:
            # Добавляем ошибку к полю
            self.add_error('color', 'Пожалуйста, выберите цвет')

        return cleaned_data


class DeliveryForm(forms.Form):
    pvz_id = forms.CharField(label='Пункт выдачи',
                             max_length=200, required=False)
    address_pvz = forms.CharField(label='Адрес',
                                  max_length=200, required=False)
