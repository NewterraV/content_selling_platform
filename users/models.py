from random import randint

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from users.services import user_directory_path


NULLABLE = {
    'null': True,
    'blank': True
}


class UserRoles(models.TextChoices):
    MEMBER = 'member', 'member'
    MODERATOR = 'moderator', 'moderator'


class User(AbstractUser):

    phone = models.CharField(
        max_length=10,
        verbose_name=_('phone'),
        unique=True
    )
    email = models.EmailField(verbose_name=_('email'))
    username = models.CharField(
        max_length=30,
        verbose_name=_('Username'),
        unique=True
        )
    first_name = models.CharField(
        max_length=50,
        verbose_name=_('first_name'),
        **NULLABLE
    )
    last_name = models.CharField(
        max_length=50,
        verbose_name=_('last_name'),
        **NULLABLE
    )
    birthday = models.DateField(
        verbose_name=_('birthday'),
    )
    is_active = models.BooleanField(
        default=False,
        verbose_name=_('verification status')
    )

    role = models.CharField(
        max_length=20,
        choices=UserRoles.choices,
        default=UserRoles.MEMBER,
        verbose_name=_('role')
    )
    avatar = models.ImageField(
        upload_to='users/avatar/',
        verbose_name=_('avatar'),
        default='default_avatar.jpg'
    )

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return f'user_{self.pk}'


class Verify(models.Model):
    """
    Модель для проверки кода верификации пользователя
    """
    user_code = models.PositiveIntegerField(
        verbose_name=_('user code'),
        **NULLABLE)
    verify_code = models.PositiveIntegerField(
        default=randint(00000, 99999),
        verbose_name=_('verify code'))
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('user'),
        related_name='verify'
    )
