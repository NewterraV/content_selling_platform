from django.db import models

from config import settings
from content.models import Content
from users.models import NULLABLE, User


class Currency(models.TextChoices):
    """Класс прессетов для валюты"""

    RUB = 'rub', '₽'
    USD = 'usd', '$'
    EUR = 'eur', '€'


class Product(models.Model):
    """
    Модель продукта

    Related:
        - pay - to model Pay
    """

    content = models.OneToOneField(
        Content,
        on_delete=models.CASCADE,
        verbose_name='Продукт',
        related_name='product',
        **NULLABLE
    )
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name='Продукт',
        related_name='product_user',
        **NULLABLE
    )

    name = models.CharField(
        max_length=150,
        verbose_name='Название'
    )

    stripe_id = models.CharField(
        max_length=100,
        verbose_name='product_stripe_id',
        **NULLABLE,
    )

    price_stripe_id = models.CharField(
        max_length=150,
        verbose_name='price_stripe_id',
        **NULLABLE,
    )

    price = models.PositiveIntegerField(
        default=49,
        verbose_name='"цена"'
    )
    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        default=Currency.RUB,
        ** NULLABLE,
        verbose_name='валюта'
    )

    def __str__(self):
        return f'product for {self.content if self.content else self.user}'


class Pay(models.Model):
    """Модель платежа пользователя"""

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='pay',
        verbose_name='платеж'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        related_name='pay',
        verbose_name='продукт',
        **NULLABLE
    )
    payment_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата платежа'
    )

    payment_amount = models.PositiveIntegerField(
        verbose_name='Сумма платежа'
    )
    payment_currency = models.CharField(
        max_length=3, verbose_name='валюта платежа', **NULLABLE,
    )
    payment_api_id = models.CharField(
        max_length=200,
        **NULLABLE,
        verbose_name='id платежа на платежном сервисе'
    )
    redirect_url = models.URLField(
        **NULLABLE,
        verbose_name='ссылка на возврат'
    )
    state = models.BooleanField(
        default=False,
        verbose_name='статус'
    )

    def __str__(self):
        return f'{self.owner} payment for a {self.product}'
