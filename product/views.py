from django.contrib.sites.shortcuts import get_current_site
from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin

from product.src.Payment import UserPayment
from subscription.models import PermanentPurchase, Subscription
from subscription.src.subscription import WorkPaidSubscription, \
    WorkSubscription


class PaymentCreateView(LoginRequiredMixin, TemplateView):
    """Представление перенаправления пользователя на страницу оплаты"""

    template_name = 'product:product_payment'
    extra_context = {
        'title': 'Оплата'
    }
    login_url = 'users:login'

    def get(self, request, *args, **kwargs):
        """Переопределение для получения ссылки на оплаты и перенаправления
        пользователя на страницу оплаты"""

        current_site = get_current_site(request)
        redirect_url = request.META.get('HTTP_REFERER')
        payment_url = UserPayment(user=request.user).create_payment(
            product_id=self.kwargs.get('pk'),
            redirect_url=redirect_url,
            domain=current_site.domain
        )
        return redirect(payment_url)


class PaymentCheckView(LoginRequiredMixin, TemplateView):
    """Представление проверки оплаты пользователя"""

    template_name = 'product:product_payment'
    extra_context = {
        'title': 'Оплата'
    }
    login_url = 'users:login'

    def get(self, request, *args, **kwargs):
        """Переопределение для определения типа продукта и его
        добавления пользователю."""

        obj = UserPayment(self.kwargs.get('pk'))
        obj.check_payment()
        if obj.state:
            if obj.product.user:
                WorkPaidSubscription(user=self.request.user).set_subs(
                    obj.product.user.pk)
                if not Subscription.objects.filter(
                        owner=self.request.user,
                        author=obj.product.user).first():
                    WorkSubscription(user=self.request.user).set_subs(
                        obj.product.user.pk)
            elif obj.product.content:
                purchase = PermanentPurchase.objects.create(
                    owner=self.request.user,
                    content=obj.product.content
                )
                purchase.save()

        return redirect(obj.payment.redirect_url)
