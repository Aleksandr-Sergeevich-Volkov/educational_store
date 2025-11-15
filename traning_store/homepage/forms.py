from catalog.models import Brend, SizeDetail
from django import forms

from .models import Comment


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={"rows": 5, "cols": 20})
        }


class SearchForm(forms.Form):
    query = forms.CharField(label='Поиск', max_length=100)


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
            self.add_measurement_fields_simple()

    def add_measurement_fields_simple(self):
        """Простая проверка - используем первый непустой размер как образец"""
        # Ищем первый размер, у которого есть данные
        sample_size = SizeDetail.objects.filter(
            size__brand=self.brand
        ).exclude(
            ankle_circumference__isnull=True
        ).first()

        if not sample_size:
            return

        measurement_fields = [
            'ankle_circumference',
            'calf_circumference',
            'circumference_under_knee',
            'mid_thigh_circumference',
            'Upper_thigh_circumference'
        ]

        for field_name in measurement_fields:
            field_value = getattr(sample_size, field_name)

            # Проверяем, что поле не пустое и имеет валидный диапазон
            if (field_value and hasattr(field_value, 'lower') and hasattr(field_value, 'upper') and field_value.lower is not None and field_value.upper is not None):

                field = SizeDetail._meta.get_field(field_name)

                self.fields[field_name] = forms.IntegerField(
                    label=field.verbose_name,
                    min_value=10,
                    max_value=150,
                    widget=forms.NumberInput(attrs={
                        'class': 'form-control',
                        'placeholder': 'Введите см'
                    })
                )
