from catalog.models import Brend, SizeDetail
from django import forms

from .models import City, Comment


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={"rows": 5, "cols": 20})
        }


class SearchForm(forms.Form):
    query = forms.CharField(
        label='Поиск',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Название, артикул или бренд...',
            'class': 'form-control',
            'id': 'search-input',  # ← ВАЖНО: добавляем этот ID
            'autocomplete': 'off',  # ← Отключаем автодополнение браузера
        })
    )


class AutocompleteForm(forms.Form):
    term = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'autocomplete-input',
            'autocomplete': 'off'
        })
    )


class SizeFinderForm(forms.Form):
    brand = forms.ModelChoiceField(
        queryset=Brend.objects.all(),
        label='Бренд',
        empty_label="Выберите бренд",
        widget=forms.Select(attrs={
            'class': 'form-control',
            'onchange': 'updateMeasurementFields()'
        })
    )


class SmartMeasurementForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.brand = kwargs.pop('brand', None)
        super().__init__(*args, **kwargs)

        if self.brand:
            self.add_measurement_fields_with_ranges()

    def add_measurement_fields_with_ranges(self):
        """Добавляет поля с выпадающими списками диапазонов"""
        brand_sizes = SizeDetail.objects.filter(size__brand=self.brand)
        if not brand_sizes.exists():
            return

        fields_config = {
            'ankle_circumference': 'Обхват щиколотки (см)',
            'calf_circumference': 'Обхват икры (см)',
            'mid_thigh_circumference': 'Обхват середины бедра (см)',
            'circumference_under_knee': 'Обхват под коленом (см)',
            'Upper_thigh_circumference': 'Обхват бедра верхний (см)'
        }

        for field_name, label in fields_config.items():
            # Получаем все уникальные диапазоны для поля
            choices = self.get_range_choices(brand_sizes, field_name)

            if choices:
                self.fields[field_name] = forms.ChoiceField(
                    label=label,
                    choices=[('', 'Выберите диапазон')] + choices,
                    widget=forms.Select(attrs={
                        'class': 'form-control',
                        'required': True
                    })
                )

    def get_range_choices(self, brand_sizes, field_name):
        """Извлекает уникальные диапазоны для выпадающего списка"""
        ranges = []
        seen = set()

        for size_detail in brand_sizes:
            field_value = getattr(size_detail, field_name)

            if (field_value and hasattr(field_value, 'lower') and hasattr(field_value, 'upper') and field_value.lower is not None and field_value.upper is not None):

                # Создаем ключ диапазона для проверки уникальности
                range_key = f"{field_value.lower}-{field_value.upper}"

                if range_key not in seen:
                    seen.add(range_key)
                    # Сохраняем как (значение для отправки, отображаемый текст)
                    ranges.append((range_key, f"{field_value.lower}-{field_value.upper} см"))

        # Сортируем по нижней границе
        ranges.sort(key=lambda x: int(x[0].split('-')[0]))
        return ranges


class CitySelectForm(forms.Form):
    city = forms.ModelChoiceField(
        queryset=City.objects.filter(is_active=True).order_by('name'),
        empty_label="Выберите город",
        widget=forms.Select(attrs={
            'class': 'city-select',
            'onchange': 'this.form.submit()'
        })
    )
