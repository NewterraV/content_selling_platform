from abc import ABC, abstractmethod
from typing import Any

from subscription.models import PaidSubscription, Subscription, \
    ServiceSubscription
from users.models import User


class WorkSubscriptionBase(ABC):
    """Базовый класс для подписок"""

    def set_subs(self, pk: str) -> bool:
        """
        Метод меняет состояние подписки на пользователя
        :param pk: pk автора
        :return: bool со статусом нового состояния подписки
        """
        if self.subs_examples.filter(author=pk):
            self.subs_examples.get(author=pk).delete()
            return False

        self.model.objects.create(
            owner=self.user,
            author=User.objects.get(pk=pk)
        )
        return True

    @staticmethod
    def subs_status(user: Any, author: str) -> dict:
        """
        Запрос возвращает статус подписок пользователя на автора
        :param user: пользователь
        :param author: PK автора
        :return: Словарь со статусом подписки
        """

        data = {
            'subs': user.subs.filter(author=author).exists(),
            'paid_subs': user.paid_subs.filter(author=author).exists(),
            'src_subs': user.src_subs.filter(owner=user).exists(),
        }
        return data


class WorkSubscription(WorkSubscriptionBase):
    """Класс для работы с бесплатными подписками"""

    def __init__(self, user: Any):
        """
        Класс для работы с бесплатными подписками
        :param user: Экземпляр пользователя
        """
        self.model = Subscription
        self.user = user
        self.subs_examples = self.user.subs


class WorkPaidSubscription(WorkSubscriptionBase):
    """Класс для работы с платными подписками на пользователя"""

    def __init__(self, user):
        self.model = PaidSubscription
        self.user = user
        self.subs_examples = self.user.paid_subs


class WorkServiceSubscription(WorkSubscriptionBase):
    """Класс для работы с подписками на сервис"""

    def __init__(self, user):
        self.model = ServiceSubscription
        self.user = user
        self.subs_examples = self.user.src_subs
