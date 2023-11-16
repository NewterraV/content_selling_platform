from django.db import models

from config import settings
from content.models import Content


class Subscription(models.Model):
    """Модель бесплатной подписки пользователя на другого пользователя"""

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Владелец',
        related_name='subs'
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'бесплатная подписка'
        verbose_name_plural = 'бесплатные подписки'


class PaidSubscription(models.Model):
    """Модель бесплатной подписки пользователя на другого пользователя"""

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Владелец',
        related_name='paid_subs'
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='paid_subscribers',
        verbose_name='Автор'
    )
    start_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'


class ServiceSubscription(models.Model):
    """Модель бесплатной подписки пользователя на другого пользователя"""

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Владелец',
        related_name='src_subs'
    )

    start_time = models.DateTimeField(auto_now_add=True)

    # product = models.ForeignKey(Product, related_name='paid_subs',
    #                             verbose_name='продукт')

    class Meta:
        verbose_name = 'подписка на сервис'
        verbose_name_plural = 'подписки на сервис'


class PermanentPurchase(models.Model):

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Владелец',
        related_name='purchases'
    )

    content = models.ForeignKey(
        Content,
        on_delete=models.CASCADE,
        verbose_name='Контент',
        related_name='purchases'
    )
