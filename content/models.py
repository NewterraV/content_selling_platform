from django.db import models

from users.models import User

NULLABLE = {
    'null': True,
    'blank': True
}


class Content(models.Model):
    """
    Модель описывающая запись пользователя
    """

    title = models.CharField(max_length=100, verbose_name='заголовок')
    description = models.TextField(verbose_name='описание')
    image = models.ImageField(
        upload_to='content/content/',
        verbose_name='изображение',
        **NULLABLE
    )
    date_update = models.DateTimeField(
        auto_now=True,
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
    is_r = models.BooleanField(
        default=False,
        verbose_name='контент 18+'
    )
    view_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Количество просмотров'
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Владелец',
        related_name='Content',
        **NULLABLE
    )


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
    image = models.ImageField(upload_to='content/video/',
                              verbose_name='превью')
