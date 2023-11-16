from django.urls import path
from product.apps import ProductConfig
from product.views import PaymentCreateView, PaymentCheckView

app_name = ProductConfig.name

urlpatterns = [
    path(
        'payment/<int:pk>/check/',
        PaymentCheckView.as_view(),
        name='payment_check'
    ),
    path(
        'product/<int:pk>/payment',
        PaymentCreateView.as_view(),
        name='product_payment'
    ),

]
