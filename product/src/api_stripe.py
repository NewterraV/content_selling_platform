from typing import Any
import stripe

from config import settings
from content.src.base import BaseAPI
from product.models import Product, Pay
from users.models import User


class APIStripe(BaseAPI):
    """Класс для работы с API Stripe"""

    def __init__(self):
        """
        Класс для работы с API Stripe
        """

        self.token = settings.STRIPE_API_KEY

    def create_product(self, name: str, price: int, currency: str, ) -> dict:
        """
        Метод создает продукт и цену на платежном сервисе
        """

        # Создание продукта
        stripe.api_key = self.token
        price_data = {
            'unit_amount': price * 100,
            "currency": currency,
        }
        # запрос к API
        response = stripe.Product.create(name=name,
                                         default_price_data=price_data)

        return {'product_id': response['id'],
                'price_id': response['default_price']}

    def get_payment_link(self, redirect_url: str) -> dict:
        """
        Метод генерирует ссылку на оплату продукта
        :param redirect_url:
        :return:
        """

        params = {
            'success_url': redirect_url,
            'line_items': [
                {
                    'price': self.product.stripe_price_id,
                    "quantity": 1
                }
            ],
            'mode': 'payment'
        }

        stripe.api_key = settings.STRIPE_API_KEY
        response = stripe.checkout.Session.create(**params)

        return {'id': response['id'], 'url': response['url']}

    # def get_payment_status(self, payment_id):
    #     """Метод проверяет статус платежа"""
    #     payment = Pay.objects.get(id=pk)
    #     stripe.api_key = self.token
    #     response = stripe.checkout.Session.retrieve(payment.payment_api_id)
    #     if response["payment_status"] == 'unpaid':
    #         return False
    #     return True


class APIStripeMixin:
    """Миксин класс APIStripe"""
    def __init__(self):
        self.stripe = APIStripe()
