from django.contrib.auth import logout as auth_logout
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import generic
from .form import Register_form


class SignUp(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'


def logout_view(request):
    auth_logout(request)
    return render(request, 'registration/logged_out.html')
