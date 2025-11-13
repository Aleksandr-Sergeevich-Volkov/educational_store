from catalog.models import Brend
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


class VenoteksMeasurementForm(forms.Form):
    ankle_circumference = forms.IntegerField(
        label='Обхват щиколотки (см)',
        min_value=10,
        max_value=100,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите см'
        })
    )
    calf_circumference = forms.IntegerField(
        label='Обхват икры (см)',
        min_value=10,
        max_value=100,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите см'
        })
    )
    mid_thigh_circumference = forms.IntegerField(
        label='Обхват середины бедра (см)',
        min_value=10,
        max_value=100,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите см'
        })
    )


class ORTOMeasurementForm(forms.Form):
    ankle_circumference = forms.IntegerField(
        label='Обхват щиколотки (см)',
        min_value=10,
        max_value=100,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите см'
        })
    )
    calf_circumference = forms.IntegerField(
        label='Обхват икры (см)',
        min_value=10,
        max_value=100,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите см'
        })
    )
    circumference_under_knee = forms.IntegerField(
        label='Обхват под коленом (см)',
        min_value=10,
        max_value=100,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите см'
        })
    )
    mid_thigh_circumference = forms.IntegerField(
        label='Обхват середины бедра (см)',
        min_value=10,
        max_value=100,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите см'
        })
    )
    upper_thigh_circumference = forms.IntegerField(
        label='Обхват бедра верхний (см)',
        min_value=10,
        max_value=100,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите см'
        })
    )


class TrivesMeasurementForm(forms.Form):
    ankle_circumference = forms.IntegerField(
        label='Обхват щиколотки (см)',
        min_value=10,
        max_value=100,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите см'
        })
    )
    calf_circumference = forms.IntegerField(
        label='Обхват икры (см)',
        min_value=10,
        max_value=100,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите см'
        })
    )
    circumference_under_knee = forms.IntegerField(
        label='Обхват под коленом (см)',
        min_value=10,
        max_value=100,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите см'
        })
    )

    upper_thigh_circumference = forms.IntegerField(
        label='Обхват бедра верхний (см)',
        min_value=10,
        max_value=100,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите см'
        })
    )
