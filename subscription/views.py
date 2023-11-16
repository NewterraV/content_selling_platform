from django.urls import reverse
from django.http import HttpResponse, HttpResponseNotModified

from django.shortcuts import render, redirect

from subscription.models import Subscription
from subscription.src.subscription import WorkSubscription
from users.models import User


def subscribe(request, pk):
    """
    Представление функции активации/деактивации подписки на обновления автора
    Args:
        request: Тело запроса
        pk: id экземпляра

    Returns:
        Собранный ответ на основе запроса
    """
    if request.user.is_anonymous:
        return redirect('users:login')
    response = WorkSubscription(user=request.user).set_subs(pk=pk)

    return HttpResponse(status=201 if response else 500)
