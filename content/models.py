from django.db import models

from config import settings
from users.models import NULLABLE
from users.services import user_directory_path_content


class Content(models.Model):
    """
    Модель описывающая запись пользователя

    Related:
        - product - to model Product
        - purchases - to model PermanentPurchase

    """
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Владелец',
        related_name='Content',
        **NULLABLE
    )
    title = models.CharField(max_length=100, verbose_name='заголовок')
    description = models.TextField(verbose_name='описание')
    image = models.ImageField(
        upload_to=user_directory_path_content,
        verbose_name='изображение', default=None
    )
    date_update = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата последнего обновления'
    )
    start_publish = models.DateTimeField(
        default=None,
        verbose_name='Дата и время публикации',
        **NULLABLE
    )
    is_publish = models.BooleanField(
        default=False,
        verbose_name='публичный доступ'
    )
    is_free = models.BooleanField(
        default=True,
        verbose_name='Бесплатный контент'
    )
    is_paid_subs = models.BooleanField(
        default=False,
        verbose_name='Контент в подписке на пользователя'
    )
    is_src_subs = models.BooleanField(
        default=False,
        verbose_name='Контент в подписке на сервис'
    )
    is_purchase = models.BooleanField(
        default=False,
        verbose_name='Доступно для приобретения в коллекцию'
    )
    view_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Количество просмотров'
    )

    def __str__(self):
        return f'{self.title}-{self.owner}'


class Video(models.Model):
    """Модель описывающая видео"""

    content = models.OneToOneField(
        Content,
        on_delete=models.CASCADE,
        verbose_name='контент',
        related_name='video')
    url = models.URLField(verbose_name='ссылка на видео')
    video_id = models.CharField(max_length=150, verbose_name='ID видео',
                                **NULLABLE)

    def __str__(self):
        return f'video to {self.content}'
