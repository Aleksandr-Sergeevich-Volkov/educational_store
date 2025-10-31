from catalog.models import Color, Model_type, Size
from django import forms

PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 7)]


class CartAddProductForm(forms.Form):
    quantity = forms.TypedChoiceField(label='Кол-во', choices=PRODUCT_QUANTITY_CHOICES,
                                      coerce=int)
    update = forms.BooleanField(required=False, initial=False,
                                widget=forms.HiddenInput)
    size = forms.ModelChoiceField(label='Размер',
                                  queryset=Size.objects.none(), required=False,
                                  # initial=Size.objects.get(id='4')
                                  )
    color = forms.ModelChoiceField(label='Цвет',
                                   queryset=Color.objects.none(),
                                   required=False,
                                   )
    m_type = forms.ModelChoiceField(label='Тип',
                                    queryset=Model_type.objects.none(),
                                    required=False,
                                    )

    def __init__(self, *args, **kwargs):
        product = kwargs.pop('product', None)
        super().__init__(*args, **kwargs)

        if product:
            # Получаем доступные цвета для этого продукта
            available_colors = product.Color.all()

            # Настраиваем поле цвета в зависимости от количества доступных цветов
            if available_colors.exists():
                self.fields['color'].queryset = available_colors
                if available_colors.count() == 1:
                    single_color = available_colors.first()
                    self.fields['color'].initial = single_color
                    self.fields['color'].widget = forms.HiddenInput()
                else:
                    # Если несколько цветов - показываем выбор
                    self.fields['color'].queryset = available_colors
                    self.fields['color'].empty_label = "Выберите цвет"
            else:
                # Если нет доступных цветов - скрываем поле
                self.fields['color'].widget = forms.HiddenInput()

        if product.brand:
            self.fields['m_type'].queryset = Model_type.objects.filter(
                brand=product.brand
            )
            self.fields['size'].queryset = Size.objects.filter(
                brand=product.brand
            )


class DeliveryForm(forms.Form):
    pvz_id = forms.CharField(label='Пункт выдачи',
                             max_length=200, required=False)
    address_pvz = forms.CharField(label='Адрес',
                                  max_length=200, required=False)
