from abc import ABC
from typing import Any

from product.src.api_stripe import APIStripe
from product.models import Product, Pay


class ProductBase(ABC):
    pass


class PaymentBase(ABC):
    pass


class UserProduct(ProductBase):

    def __init__(self, pk: str = None):
        """
        Класс для работы с продуктом
        :param pk: pk продукта (экземпляра модели Product)
        """
        self.stripe = APIStripe()
        if pk:
            self.product = Product.objects.get(id=pk)
            self.price = self.product.price
            self.currency = self.product.currency
            if self.product.content:
                self.name = self.product.content.title
            else:
                self.name = (f'Месячная подписка на пользователя '
                             f'{self.product.user.username}')

    def create_ids_product(self) -> None:
        """
        Метод добавляет id продукта на платежном сервисе в модель
        """

        ids = self.stripe.create_product(
            name=self.name,
            price=self.price,
            currency=self.currency
        )
        print(ids)

        self.product.stripe_id = ids['product_id']
        self.product.price_stripe_id = ids['price_id']
        self.product.save()


class UserPayment(PaymentBase):

    def __init__(self, pk: str = None, user: Any = None):
        self.stripe = APIStripe()
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
