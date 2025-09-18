from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=64, label='Почта', help_text='Обязательное поле. Введите действующий email.')
    first_name = forms.CharField(required=False, max_length=32, label='Имя')
    last_name = forms.CharField(required=False, max_length=32, label='Фамилия')

    def clean_email(self):
        email = self.cleaned_data.get('email', '')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Эта почта уже зарегестрированна')

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        labels = {'username': 'Покупатель', 'email': 'Почта', 'first_name': 'Имя', 'last_name': 'Фамилия',
                  'password1': 'Пароль',
                  'password2': 'Повторить пароль'
                  }

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})


class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username',)
