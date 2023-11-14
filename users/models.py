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
        verbose_name='Телефон',
        unique=True
    )
    username = models.CharField(
        max_length=30,
        verbose_name='Псевдоним',
        unique=True
    )
    email = models.EmailField(verbose_name=_('email'))
    first_name = models.CharField(
        max_length=50,
        verbose_name='Имя',
        **NULLABLE
    )
    last_name = models.CharField(
        max_length=50,
        verbose_name='Фамилия',
        **NULLABLE
    )
    birthday = models.DateField(
        verbose_name='День рождения',
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
        verbose_name='Аватар',
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
        verbose_name='user code',
        **NULLABLE)
    verify_code = models.PositiveIntegerField(
        default=randint(00000, 99999),
        verbose_name='verify code')
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name='user',
        related_name='verify'
    )
