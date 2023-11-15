from django.db import models

from config import settings
from content.models import Content
from users.models import NULLABLE


class Currency(models.TextChoices):
    RUB = 'rub', '₽ - рубли'
    USD = 'usd', '$ - доллары'
    EUR = 'eur', '€ - евро'


class Product(models.Model):
    """Модель продукта"""

    content = models.OneToOneField(
        Content,
        on_delete=models.CASCADE,
        verbose_name='Продукт',
        related_name='product',
        **NULLABLE
    )
    user = models.OneToOneField(
        Content,
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


class Price(models.Model):
    """Модель цены продукта"""

    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name='price',
        verbose_name='продукт'
    )

    price_stripe_id = models.CharField(
        max_length=100,
        verbose_name='price_stripe_id',
        **NULLABLE,
    )

    price = models.PositiveIntegerField(

    )
    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
    )


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
    payment_url = models.URLField(
        **NULLABLE,
        verbose_name='ссылка на оплату'
    )
    state = models.BooleanField(
        default=False,
        verbose_name='статус'
    )
