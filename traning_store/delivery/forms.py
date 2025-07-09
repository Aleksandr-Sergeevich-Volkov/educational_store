from django import forms


class DeliveryForm(forms.Form):
    pvz_id = forms.CharField(label='Пункт выдачи',
                             max_length=200, required=False)
    address_pvz = forms.CharField(label='Адрес',
                                  max_length=200, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['pvz_id'].widget.attrs['readonly'] = True
        self.fields['address_pvz'].widget.attrs['readonly'] = True
