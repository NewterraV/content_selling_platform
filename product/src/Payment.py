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
            self.product_id = self.product.stripe_id
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

        self.product.stripe_id = ids['product_id']
        self.product.price_stripe_id = ids['price_id']
        self.product.save()

    def update_product(self):
        """Метод обновляет продукт"""

        APIStripe().delete_product(self.product_id)
        self.create_ids_product()



class UserPayment(PaymentBase):

    def __init__(self, pk: str = None, user: Any = None):
        self.stripe = APIStripe()
        if pk:
            self.payment = Pay.objects.get(id=pk)
            self.user = self.payment.owner
            self.state = self.payment.state
            self.product = self.payment.product
        else:
            self.state = None
            self.user = user
            self.product = None

    def create_payment(self, product_id: str, redirect_url: str,
                       domain: str) -> str:
        """Метод создает запись о платеже и возвращает ссылку на оплату"""
        product = Product.objects.filter(pk=product_id).first()

        payment = Pay.objects.create(
            owner=self.user,
            product=product,
            payment_amount=product.price,
            payment_currency=product.currency,
            redirect_url=redirect_url,
        )
        payment.save()

        check_url = f'http://{domain}/product/payment/{payment.pk}/check/'

        response = self.stripe.get_payment_link(check_url,
                                                product.price_stripe_id)

        payment.payment_api_id = response['id']
        payment.save()

        return response['url']

    def check_payment(self):
        """Метод проверяет статус платежа и обновляет его в БД"""

        status = self.stripe.get_status(
            payment_id=self.payment.payment_api_id)

        self.state = status
        self.payment.state = status
        self.payment.save()
