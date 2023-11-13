from django.contrib.auth.views import LoginView as BaseLoginView, \
    LogoutView as BaselogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView

from users.forms import RegisterForm, LoginForm
from users.models import User


class UserRegisterView(CreateView):
    model = User
    form_class = RegisterForm

    success_url = reverse_lazy('content:content_list')


class LoginView(BaseLoginView):
    """Класс для представления авторизации пользователя"""
    form_class = LoginForm
    template_name = 'users/login.html'


class LogoutView(BaselogoutView):
    """Класс для представления выхода пользователя"""
    pass
