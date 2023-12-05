from django.contrib.auth.views import LoginView as BaseLoginView, \
    LogoutView as BaselogoutView
from django.views.generic import CreateView, UpdateView, TemplateView
from django.forms import inlineformset_factory
from django.db.models import Sum
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse

from content.models import Content
from product.forms import UserProductForm
from product.models import Product
from subscription.models import Subscription
from subscription.src.subscription import WorkSubscription
from users.forms import RegisterForm, LoginForm, UserUpdateForm, VerifyForm
from users.models import User, Verify
from users.services import get_client_ip
from users.src.smsru_api import APISMSru


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

    def form_valid(self, form):
        """Переопределнние для валидации и сохранения формсета"""

        formset = self.get_context_data()['formset']

        if not formset.is_valid():
            return self.form_invalid(form)

        self.object = form.save()
        formset.instance = self.object
        formset.save()

        return super().form_valid(form)


class UserDetailView(TemplateView):
    """Представление детальной информации о пользователе"""
    template_name = 'users/user_detail.html'

    def get_context_data(self, **kwargs):
        """Переопределение для вывода дополнительного контекста"""

        context_data = super().get_context_data(**kwargs)

        # Получаем основной объект
        author = User.objects.get(pk=self.kwargs.get('pk'))
        context_data['author'] = author

        # Получаем контент автора
        context_data['content_list'] = Content.objects.filter(
            owner=author, is_publish=True).order_by('-date_update')

        # Собираем сопутствующий контент
        product = Product.objects.filter(user=author).first()
        sub = {
            'subs_count': Subscription.objects.filter(
                author=author).count(),
            'view_count': Content.objects.values('view_count').filter(
                owner=author, is_publish=True).aggregate(
                Sum('view_count'))['view_count__sum'],
            'video_count': len(context_data['content_list']),
            'paid_subs_price': product.price if product else None,
            'paid_subs_currency':
                product.get_currency_display() if product else None,
            'paid_subs_pk': product.pk if product else None
        }
        context_data['sub'] = sub

        # проверяем подписки пользователя
        if self.request.user.is_authenticated:
            context_data['subs'] = WorkSubscription.subs_status(
                        self.request.user,
                        author,
                    )
        return context_data


class UserRegisterView(UserFormsetMixin, CreateView):
    """Представление регистрации пользователя"""
    model = User
    form_class = RegisterForm

    success_url = reverse_lazy('content:content_list')

    def form_valid(self, form):
        """Переопределнние для валидации и сохранения формсета"""

        formset = self.get_context_data()['formset']

        if not formset.is_valid():
            return self.form_invalid(form)
        self.object = form.save(commit=False)
        ip = get_client_ip(self.request)
        verify_code = APISMSru().get_verify_code(
            phone=f'7{self.object.phone}',
            ip_address=ip
        )
        print(verify_code)
        if not verify_code:
            return redirect(reverse(
                'content:index'))
        self.object = form.save()
        formset.instance = self.object
        formset.save()
        verify = Verify.objects.create(
            user=self.object, verify_code=verify_code)
        verify.save()
        return redirect(reverse(
            'users:verify', args=[verify.pk]))


class UserUpdateView(UserFormsetMixin, UpdateView):
    """Представление для редактирования профиля пользователя"""

    model = User
    form_class = UserUpdateForm

    success_url = reverse_lazy('content:index')

    def get_object(self, queryset=None):
        return self.request.user


class LoginView(BaseLoginView):
    """Класс для представления авторизации пользователя"""
    form_class = LoginForm
    template_name = 'users/login.html'


class LogoutView(BaselogoutView):
    """Класс для представления выхода пользователя"""
    pass


class VerifyView(UpdateView):
    """Представление проверки кода верификации"""
    model = Verify
    success_url = 'users:login'
    form_class = VerifyForm

    def form_valid(self, form):
        """Переопределение делает пользователя которому принадлежит код
        верификации активным"""

        self.object = form.save()
        user = self.object.user
        user.is_active = True
        user.save()
        self.object.delete()
        return redirect(reverse(self.success_url))


class GetVerify(TemplateView):
    """Представление для повторного запроса кода верификации"""
    model = Verify
    success_url = 'users:verify'

    def get(self, request, *args, **kwargs):

        verify = Verify.objects.get(pk=self.kwargs.get('pk'))
        user = verify.user
        ip = get_client_ip(self.request)
        verify_code = APISMSru().get_verify_code(
            phone=f'7{user.phone}',
            ip_address=ip
        )
        verify.verify_code = verify_code
        verify.save()
        return redirect(reverse(
            'users:verify', args=[verify.pk]))
