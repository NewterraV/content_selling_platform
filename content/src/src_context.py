from random import shuffle, sample
from typing import Any
from django.forms import inlineformset_factory

from content.forms import VideoForm
from content.models import Content, Video
from product.forms import ProductForm
from product.models import Product
from subscription.models import Subscription, PaidSubscription
from subscription.src.subscription import WorkSubscription


def get_index_context(context_data: dict, user: Any, ):
    """
    Вспомогательный метод для сбора контекста домашней страницы
    авторизованного пользователя
    :param context_data: контекст собранный методом get_context_data
    (основной контекст)
    :param user: Авторизованный пользователь
    :return:
    """

    # Получаем список авторов на которых бесплатно подписан пользователь
    subs_author = [obj.author.pk for obj in
                   Subscription.objects.filter(
                       owner=user)]

    # Получаем контент авторов на которых бесплатно подписан пользователь
    subs_content = list(
        Content.objects.exclude(
            owner=user).filter(owner__in=subs_author,
                               is_publish=True).order_by(
            '-date_update')) if subs_author else None

    # Получаем список авторов на которых пользователь подписан платно
    paid_subs_author = [obj.author.pk for obj in
                        PaidSubscription.objects.filter(
                            owner=user)]

    # Получаем контент авторов на которых платно подписан пользователь
    subs_paid_content = list(
        Content.objects.filter(
            owner__in=paid_subs_author,
            is_publish=True).order_by(
            '-date_update')) if subs_author else None

    # Получаем список контента который пользователь приобрел по
    # разовой покупке
    purchased = list(
        Content.objects.filter(purchases__owner=user,
                               is_publish=True))

    # Собираем контент на основе полученных данных
    # с применением методов рандомизации
    if subs_content:
        free_set = set(list(
            context_data['object_list']) + subs_content[:12])
        free_list = list(free_set)
        shuffle(free_list)
        context_data['object_list'] = free_list
    if subs_paid_content:
        context_data['subs_paid_content'] = subs_paid_content[:8]
    if purchased:
        context_data['purchased'] = sample(purchased, 4) if len(
            purchased) > 4 else purchased

    return context_data


def get_content_detail_context(context_data: dict, user: Any,
                               content: Any) -> dict:
    """
    Вспомогательный метод для сбора контекста страницы с детальной информацией
     о пользователе
    :param context_data: контекст собранный методом get_context_data
    (основной контекст)
    :param user: Текущий пользователь (request.user)
    :param content: Экземпляр модели контент
    :return:
    """
    if user.is_authenticated:
        # Проверка подписок пользователя
        context_data['subs'] = WorkSubscription.subs_status(
            user,
            content.owner,
        )
        # проверка вхождения текущего видео в купленные пользователем
        context_data['subs'][
            'purchase'] = user.purchases.filter(
            content=content)
        # проверка подписки пользователя на владельца видео
        owner_paid_subs = Product.objects.filter(
            user=content.owner).first()
        # Сборка сопровождающей информации
        sub = {
            'subs_count': Subscription.objects.filter(
                author=content.owner).count(),
            'paid_subs_price':
                owner_paid_subs.price if owner_paid_subs else None,
            'paid_subs_currency':
                (owner_paid_subs.get_currency_display()
                 if owner_paid_subs else None),
            'paid_subs_pk':
                owner_paid_subs.pk if owner_paid_subs else None
        }
        context_data['sub'] = sub

    # Проверка доступности видео для пользователя
    if content.is_free:
        context_data['video'] = content.video.video_id
    else:
        if user.is_authenticated:
            # проверка на владельца
            if user == content.owner:
                context_data['video'] = content.video.video_id
            # проверка доступности в подписке на сервис (в разработке)
            elif content.is_src_subs and context_data['subs']['src_subs']:
                context_data['video'] = content.video.video_id
            # проверка доступности в подписках пользователя
            elif (content.is_paid_subs
                  and context_data['subs']['paid_subs']):
                context_data['video'] = content.video.video_id
            # проверка вхождения текущего видео в купленные пользователем
            elif context_data['subs']['purchase']:
                context_data['video'] = content.video.video_id

    context_data['title'] = content.title
    # Сборка списка видео
    play_list = list(Content.objects.filter(is_publish=True).exclude(
        pk=content.pk))

    # Отображение 10 рандомных записей в предложенных
    context_data['play_list'] = sample(play_list, 10) if len(
        play_list) > 10 else play_list

    return context_data


def get_formset_to_create(context_data: dict, request: Any,
                          instance: Any) -> dict:
    """
    Вспомогательный метод для формирования формсета создания контента
    :param context_data: контекст собранный методом get_context_data
    (основной контекст)
    :param request: объект request(self.request)
    :param instance: (self.object)
    :return:
    """
    video_form = inlineformset_factory(Content, Video,
                                       form=VideoForm,
                                       extra=1,
                                       can_delete=False)
    product_form = inlineformset_factory(Content, Product,
                                         form=ProductForm,
                                         extra=1,
                                         can_delete=False)
    if request.method == 'POST':
        video_formset = video_form(request.POST,
                                   instance=instance)
        product_formset = product_form(request.POST,
                                       instance=instance)
    else:
        video_formset = video_form(instance=instance)
        product_formset = product_form(instance=instance)

    context_data['video_formset'] = video_formset
    context_data['product_formset'] = product_formset

    return context_data
