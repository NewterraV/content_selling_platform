from django.db import models


NULLABLE = {
    'null': True,
    'blank': True
}


class Content(models.Model):
    """
    Модель описывающая запись пользователя
    """

    title = models.CharField(max_length=150, verbose_name='заголовок')
    description = models.TextField(verbose_name='описание')
    image = models.ImageField(verbose_name='изображение', **NULLABLE)
    date_update = models.DateTimeField(
        auto_now=True,
        verbose_name='дата последнего обновления'
    )
    is_publish = models.BooleanField(
        default=False,
        verbose_name='публичный доступ'
    )
    is_r = models.BooleanField(
        default=False,
        verbose_name='контент 18+'
    )


class Video(models.Model):
    """Модель описывающая видео"""

    content = models.ForeignKey(
        Content,
        on_delete=models.SET_NULL,
        verbose_name='контент',
        related_name='video')
    url = models.URLField(verbose_name='ссылка на видео')
    image = models.ImageField(verbose_name='превью')
