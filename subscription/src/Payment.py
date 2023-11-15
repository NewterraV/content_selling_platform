from abc import ABC
from typing import Any

from product.src.api_stripe import APIStripeMixin
from product.models import Product, Pay
from users.models import User


class ProductBase(ABC):
    pass


class PaymentBase(ABC):
    pass


class UserProduct(APIStripeMixin, ProductBase):

    def __init__(self, pk: str = None):
        """
        Класс для работы с продуктом
        :param pk: pk продукта (экземпляра модели Product)
        """
        super().__init__(self)
        if pk:
            self.product = Product.objects.get(id=pk)
            self.name = self.product.name
            self.price = self.product.price
            self.currency = self.product.currency


    def create_ids_product(self) -> None:
        """
        Метод добавляет id продукта на платежном сервисе в модель
        """

        ids = self.stripe.create_product(
            name=self.name,
            price=self.price,
            currency=self.currency
        )

        self.product.stripe_id = ids['product_id']
        self.product.stripe_price_id = ids['price_id']
        self.product.save()


class UserPayment(APIStripeMixin, PaymentBase):

    def __init__(self, pk: str = None, user: Any = None):
        super().__init__(self)
        if pk:
            self.payment = Pay.objects.get(id=pk)
            self.user = self.payment.owner
        else:
            self.user = user

    def create_payment(self, product_id: str, redirect_url: str) -> str:
        """Метод создает запись о платеже и возвращает ссылку на оплату"""
        product = Product.objects.filter(pk=product_id).first()

        response = self.stripe.get_payment_link(redirect_url)

        payment = Pay.objects.create(
            owner=self.user,
            product=product,
            payment_amount=product.price,
            payment_currency=product.currency,
            payment_api_id=response['id'],
            payment_url=response['url']
        )
        payment.save()

        return response['url']
