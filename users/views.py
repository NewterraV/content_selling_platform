from django.contrib.auth.views import LoginView as BaseLoginView, \
    LogoutView as BaselogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.forms import inlineformset_factory

from product.forms import UserProductForm
from product.models import Product
from users.forms import RegisterForm, LoginForm, UserUpdateForm
from users.models import User
from product.tasks import task_create_product


class UserFormsetMixin:
    """Миксин с переопределением методов представлений"""

    def get_context_data(self, **kwargs):
        """Переопределение добавляет формсет создания продукта пользователя"""

        context_data = super().get_context_data(**kwargs)
        formset = inlineformset_factory(User, Product,
                                        form=UserProductForm,
                                        extra=1,
                                        can_delete=False)

        if self.request.method == 'POST':
            formset = formset(self.request.POST,
                              instance=self.object)
        else:
            formset = formset(instance=self.object)

        context_data['formset'] = formset
        return context_data


class UserRegisterView(UserFormsetMixin, CreateView):
    model = User
    form_class = RegisterForm

    success_url = reverse_lazy('content:content_list')

    def form_valid(self, form):
        formset = self.get_context_data()['formset']
        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
        return super().form_valid(form)


class UserUpdateView(UserFormsetMixin, UpdateView):
    """Представление для редактирования профиля пользователя"""

    model = User
    form_class = UserUpdateForm

    success_url = reverse_lazy('content:index')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        formset = self.get_context_data()['formset']
        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()

        return super().form_valid(form)


class LoginView(BaseLoginView):
    """Класс для представления авторизации пользователя"""
    form_class = LoginForm
    template_name = 'users/login.html'


class LogoutView(BaselogoutView):
    """Класс для представления выхода пользователя"""
    pass
