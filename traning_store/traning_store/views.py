from urllib.parse import urlparse

from catalog.forms import SignUpForm
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import is_valid_path, reverse_lazy
from django.views.generic.edit import CreateView


class SomeEntityCreateView(CreateView):
    template_name = 'registration/registration_form.html'
    form_class = SignUpForm
    success_url = reverse_lazy('homepage:homepage')


def login_view(request):
    next_url = request.META.get('HTTP_REFERER')

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Ensure next_url is safe or default to home page
            next_url = request.POST.get('next', next_url)
            parsed_url = urlparse(next_url)
            print(parsed_url)
            if not parsed_url.netloc and is_valid_path(next_url):
                return HttpResponseRedirect(next_url)
            return HttpResponseRedirect(next_url)
    else:
        form = AuthenticationForm()

    return render(request, 'registration/login.html', {'form': form, 'next': next_url})


def logout_view(request):
    logout(request)
    return redirect('/')
