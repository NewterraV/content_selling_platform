from django.contrib.sites.shortcuts import get_current_site
from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin

from product.models import Product, Pay
from product.src.Payment import UserProduct, UserPayment
from subscription.models import PermanentPurchase
from subscription.src.subscription import WorkPaidSubscription


class PaymentCreateView(LoginRequiredMixin, TemplateView):
    template_name = 'product:product_payment'
    extra_context = {
        'title': 'Оплата'
    }
    login_url = 'users:login'

    def get(self, request, *args, **kwargs):
        current_site = get_current_site(request)
        redirect_url = request.META.get('HTTP_REFERER')
        payment_url = UserPayment(user=request.user).create_payment(
            product_id=self.kwargs.get('pk'),
            redirect_url=redirect_url,
            domain=current_site.domain
        )
        return redirect(payment_url)


class PaymentCheckView(LoginRequiredMixin, TemplateView):
    template_name = 'product:product_payment'
    extra_context = {
        'title': 'Оплата'
    }
    login_url = 'users:login'

    def get(self, request, *args, **kwargs):

        obj = UserPayment(self.kwargs.get('pk'))
        obj.check_payment()
        print(obj.state)
        if obj.state:
            if obj.product.user:
                WorkPaidSubscription(user=self.request.user).set_subs(
                    obj.product.user.pk)
            elif obj.product.content:
                purchase = PermanentPurchase.objects.create(
                    owner=self.request.user,
                    content=obj.product.content
                )
                purchase.save()

        return redirect(obj.payment.redirect_url)
