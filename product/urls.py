from django.urls import path
from product.apps import ProductConfig
from product.views import ProductView, PaymentView

app_name = ProductConfig.name

urlpatterns = [
    path(
        'payment/<int:pk>/check/',
        PaymentView.as_view(),
        name='payment_check'
    ),
    path(
        'product/<int:pk>/payment',
        ProductView.as_view(),
        name='product_payment'
    ),

]
