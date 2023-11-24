from django.forms import inlineformset_factory
from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.http import Http404
from django.views.generic import (
    ListView,
    DetailView,
    DeleteView,
    CreateView,
    UpdateView
)

from content.forms import ContentForm, ContentUpdateForm
from content.models import Content

from content.src.src_context import get_index_context, \
    get_content_detail_context, get_formset_to_create
from content.tasks import task_get_image, task_delete_img
from product.forms import ProductForm
from product.models import Product
from product.tasks import task_create_product, task_delete_product


class IndexView(ListView):
    """Вывод главной страницы"""

    model = Content
    template_name = 'content/index.html'

    def get_queryset(self):
        """Переопределение для сбора ограниченного количества видео"""
        if self.request.user.is_authenticated:
            queryset = super().get_queryset().exclude(
                owner=self.request.user).order_by('?').filter(
                is_publish=True)[:12]
        else:
            queryset = super().get_queryset().order_by('?').filter(
                is_publish=True)[:12]

        return queryset

    def get_context_data(self, **kwargs):
        """Переопределение для расширения контекста домашней страницы"""

        context_data = super().get_context_data(**kwargs)
        context_data['title'] = 'NewTerra'

        if self.request.user.is_authenticated:
            context_data = get_index_context(
                context_data=context_data, user=self.request.user
            )

        return context_data


class ContentDetailView(DetailView):
    """
    Контроллер для отображения детальной информации об экземпляре контента.
    """
    model = Content

    def get_context_data(self, **kwargs):
        """Переопределение метода для формирования необходимого
        дополнительного контекста"""

        context_data = super().get_context_data(**kwargs)

        context_data = get_content_detail_context(
            context_data=context_data,
            user=self.request.user,
            content=self.object,
        )

        return context_data

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
        """Переопределение для выборки из контента
         принадлежащего пользователю"""
        queryset = super().get_queryset().filter(
            owner=self.request.user).order_by('-date_update')
        return queryset


class ContentCreateView(LoginRequiredMixin, CreateView):
    """Представление для создания контента"""
    model = Content
    form_class = ContentForm
    login_url = 'users:login'
    extra_context = {
        'title': 'Создание контента'
    }

    success_url = reverse_lazy('content:content_list')

    def get_form_kwargs(self, **kwargs):
        """Метод передает авторизованного пользователя в kwargs"""
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def get_context_data(self, **kwargs):
        """Переопределение добавляет формсет содержания контента"""

        context_data = super().get_context_data(**kwargs)

        context_data = get_formset_to_create(
            context_data=context_data,
            request=self.request,
            instance=self.object
        )

        return context_data
    
    def form_valid(self, form):
        """Переопределение для добавления владельца и проверки наличия
        обложки видео"""

        product_formset = self.get_context_data()['product_formset']
        video_formset = self.get_context_data()['video_formset']

        if not video_formset.is_valid() or not product_formset.is_valid():
            return self.form_invalid(form)

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


class ContentUpdateView(LoginRequiredMixin, UpdateView):
    """Представление для обновления контента"""
    model = Content
    form_class = ContentUpdateForm
    login_url = 'users:login'
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
            if not formset.is_valid():
                return self.form_invalid(form)
            if formset.is_valid():
                self.object = form.save()
                formset.instance = self.object
                formset.save()
                task_create_product.delay(self.object.product.pk)
        if self.object.is_free:
            product = Product.objects.filter(content=self.object).first()
            if product:
                task_delete_product.delay(self.object.product.stripe_id)
                product.delete()
        return super().form_valid(form)


class ContentDeleteView(LoginRequiredMixin, DeleteView):
    """Представление для удаления контента"""

    model = Content
    success_url = reverse_lazy('content:content_list')
    login_url = 'users:login'
    extra_context = {
        'title': 'Подтверждение удаления'
    }

    def form_valid(self, form):
        """Переопределение для удаления файлов связанных с контентом"""
        if self.request.user == self.object.owner:
            if self.object.is_purchase:
                task_delete_product.delay(self.object.product.stripe_id)
            if self.object.image:
                task_delete_img.delay(path_to=str(self.object.image))
            return super().form_valid(form)
        raise Http404('Вы не являетесь владельцем данного контента')
