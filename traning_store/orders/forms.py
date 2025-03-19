from django import forms
from .models import Order
import logging
logger = logging.getLogger(__name__)


class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'address', 'address_pvz','postal_code', 'city']

    """ def __init__(self, *args, **kwargs):
        super(OrderCreateForm, self).__init__(*args, **kwargs)
        if self.fields['address'] is not None:
            logger.warning(type(self.fields['address'])) 
            self.fields['postal_code'].initial = 'заполнен адрес пункта выдачи' """ """
    
    def clean(self):
 
        # data from the form is fetched using super function
        super(OrderCreateForm, self).clean()
         
        # extract the username and text field from the data
        cleaned_data = super().clean()
        cleaned_data['postal_code'].initial = 'заполнен адрес пункта выдачи'
        return cleaned_data
        address = self.cleaned_data.get('address')
        logger.warning(address)  
 
        # conditions to be met for the username length
        #if address is not None:
        self.fields['postal_code'].initial = 'заполнен адрес пункта выдачи'
 
        # return any errors if found
        return self.cleaned_data """