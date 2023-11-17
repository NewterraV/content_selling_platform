from django.forms import inlineformset_factory
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.db.models import Q
from django.views.generic import (
    ListView,
    DetailView,
    DeleteView,
    CreateView,
    UpdateView
)

from content.forms import VideoForm, ContentForm, ContentUpdateForm
from content.models import Content, Video
from random import sample, shuffle
from django.shortcuts import redirect

from content.tasks import task_get_image, task_delete_img
from product.forms import ProductForm
from product.models import Product
from product.tasks import task_create_product, task_delete_product
from subscription.models import Subscription, PaidSubscription
from subscription.src.subscription import WorkSubscription


class ContentFormsetMixin:
    """
    Миксин добавляющий формсет для классов создания и обновления рассылки
    """
    extra = 1

    def get_context_data(self, **kwargs):
        """Переопределение добавляет формсет содержания контента"""

        context_data = super().get_context_data(**kwargs)
        video_form = inlineformset_factory(Content, Video,
                                           form=VideoForm,
                                           extra=self.extra,
                                           can_delete=False)
        product_form = inlineformset_factory(Content, Product,
                                             form=ProductForm,
                                             extra=self.extra,
                                             can_delete=False)
        if self.request.method == 'POST':
            video_formset = video_form(self.request.POST,
                                       instance=self.object)
            product_formset = product_form(self.request.POST,
                                           instance=self.object)
        else:
            video_formset = video_form(instance=self.object)
            product_formset = product_form(instance=self.object)

        context_data['video_formset'] = video_formset
        context_data['product_formset'] = product_formset
        return context_data


class IndexView(ListView):
    """Вывод главной страницы"""

    model = Content
    template_name = 'content/index.html'

    def get_queryset(self):
        if self.request.user.is_authenticated:
            queryset = super().get_queryset().exclude(
                owner=self.request.user).filter(
                is_publish=True, is_free=True)[:12]
        else:
            queryset = super().get_queryset().filter(
                is_publish=True, is_free=True)[:12]

        return queryset

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['title'] = 'NewTerra'

        if self.request.user.is_authenticated:
            subs_author = [obj.author.pk for obj in
                           Subscription.objects.filter(
                               owner=self.request.user)]

            subs_content = list(
                self.model.objects.exclude(
                    owner=self.request.user).filter(owner__in=subs_author,
                                                    is_publish=True).order_by(
                    '-date_update')) if subs_author else None

            paid_subs_author = [obj.author.pk for obj in
                                PaidSubscription.objects.filter(
                                    owner=self.request.user)]

            subs_paid_content = list(
                self.model.objects.filter(
                    owner__in=paid_subs_author,
                    is_publish=True).order_by(
                    '-date_update')) if subs_author else None

            purchased = list(
                self.model.objects.filter(purchases__owner=self.request.user,
                                          is_publish=True))
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


class ContentDetailView(DetailView):
    """
    Контроллер для отображения детальной информации об экземпляре контента.
    """
    model = Content

    def get_context_data(self, **kwargs):
        """Переопределение метода для формирования необходимого
        дополнительного контекста"""

        context = super().get_context_data(**kwargs)
        # Сборка дополнительного контента для страницы
        if self.request.user.is_authenticated:
            # Проверка подписок пользователя
            context['subs'] = WorkSubscription.subs_status(
                self.request.user,
                self.object.owner,
            )
            # проверка вхождения текущего видео в купленные пользователем
            context['subs'][
                'purchase'] = self.request.user.purchases.filter(
                content=self.object)
            # проверка подписки пользователя на владельца видео
            owner_paid_subs = Product.objects.filter(
                user=self.object.owner).first()
            # Сборка сопровождающей информации
            sub = {
                'subs_count': Subscription.objects.filter(
                    author=self.object.owner).count(),
                'paid_subs_price':
                    owner_paid_subs.price if owner_paid_subs else None,
                'paid_subs_currency':
                    (owner_paid_subs.get_currency_display()
                     if owner_paid_subs else None),
                'paid_subs_pk': owner_paid_subs.pk if owner_paid_subs else None
            }
            context['sub'] = sub

        # Проверка доступности видео для пользователя
        if self.object.is_free:
            context['video'] = self.object.video.video_id
        else:
            if self.request.user.is_authenticated:
                # проверка на владельца
                if self.request.user == self.object.owner:
                    context['video'] = self.object.video.video_id
                # проверка доступности в подписке на сервис (в разработке)
                elif self.object.is_src_subs and context['subs']['src_subs']:
                    context['video'] = self.object.video.video_id
                # проверка доступности в подписках пользователя
                elif (self.object.is_paid_subs
                      and context['subs']['paid_subs']):
                    context['video'] = self.object.video.video_id
                # проверка вхождения текущего видео в купленные пользователем
                elif context['subs']['purchase']:
                    context['video'] = self.object.video.video_id
                print(context['sub'])

        context['title'] = self.object.title
        # Сборка списка видео
        play_list = list(self.model.objects.filter(is_publish=True).exclude(
            pk=self.object.pk))

        # Отображение 10 рандомных записей в предложенных
        context['play_list'] = sample(play_list, 10) if len(
            play_list) > 10 else play_list

        return context

    def get_object(self, queryset=None):
        """Переопределение реализует счетчик просмотров"""
        obj = super().get_object(queryset)
        obj.view_count += 1
        obj.save()
        return obj


class ContentListView(LoginRequiredMixin, ListView):
    """Контроллер для отображения списка контента"""

    model = Content
    extra_context = {'title': 'Мой контент'}
    login_url = 'users:login'

    def get_queryset(self):
        queryset = super().get_queryset().filter(owner=self.request.user)
        return queryset


class ContentCreateView(ContentFormsetMixin, CreateView):
    model = Content
    form_class = ContentForm

    extra_context = {
        'title': 'Создание контента'
    }

    success_url = reverse_lazy('content:content_list')

    def get_form_kwargs(self, **kwargs):
        """Метод передает авторизованного пользователя в kwargs"""
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        """Переопределение для добавления владельца и проверки наличия
        обложки видео"""

        product_formset = self.get_context_data()['product_formset']
        video_formset = self.get_context_data()['video_formset']

        if video_formset.is_valid():
            form.instance.owner = self.request.user
            self.object = form.save()
            if not self.object.image:
                task_get_image.delay(pk=self.object.pk)
            video_formset.instance = self.object
            video_formset.save()
            if self.object.is_purchase:
                if product_formset.is_valid():
                    product_formset.instance = self.object
                    product_formset.save()
                    task_create_product.delay(self.object.product.pk)

        return super().form_valid(form)


class ContentUpdateView(UpdateView):
    model = Content
    form_class = ContentUpdateForm

    extra_context = {
        'title': 'Обновление контента'
    }

    success_url = reverse_lazy('content:content_list')

    def get_form_kwargs(self, **kwargs):
        """Метод передает авторизованного пользователя в kwargs"""
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def get_success_url(self):
        """Переопределение для перенаправления после редактирования
        контента"""
        return reverse(
            'content:content_detail',
            args=[self.kwargs.get('pk')]
        )

    def get_context_data(self, **kwargs):
        """Переопределение добавляет формсет цены контента"""

        context_data = super().get_context_data(**kwargs)

        formset = inlineformset_factory(Content, Product,
                                        form=ProductForm,
                                        extra=1,
                                        can_delete=False)
        if self.request.method == 'POST':
            product_formset = formset(self.request.POST,
                                      instance=self.object)
        else:
            product_formset = formset(instance=self.object)

        context_data['product_formset'] = product_formset
        return context_data

    def form_valid(self, form):
        """Переопределение для сохранения формсета"""
        formset = self.get_context_data()['product_formset']
        if self.object.is_purchase:
            if formset.is_valid():
                self.object = form.save()
                formset.instance = self.object
                formset.save()
                print(self.object.product.pk)
                task_create_product.delay(self.object.product.pk)
        if self.object.is_free:
            product = Product.objects.filter(content=self.object).first()
            if product:
                task_delete_product.delay(self.object.product.stripe_id)
                product.delete()
        return super().form_valid(form)


class ContentDeleteView(DeleteView):
    """Представление для удаления контента"""

    model = Content
    success_url = reverse_lazy('content:content_list')
    extra_context = {
        'title': 'Подтверждение удаления'
    }

    def form_valid(self, form):
        """Переопределение для удаления файлов связанных с контентом"""
        if self.object.is_purchase:
            task_delete_product.delay(self.object.product.stripe_id)
        if self.object.image:
            task_delete_img.delay(path_to=str(self.object.image))
        return super().form_valid(form)
