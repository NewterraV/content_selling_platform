from django.forms import inlineformset_factory
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.db.models import F
from django.views.generic import (
    ListView,
    DetailView,
    DeleteView,
    CreateView,
    UpdateView,
    TemplateView
)

from content.forms import VideoForm, ContentForm, ContentUpdateForm
from content.models import Content, Video
from random import sample

from content.tasks import task_get_image, task_delete_img


class ContentFormsetMixin:
    """
    Миксин добавляющий формсет для классов создания и обновления рассылки
    """
    extra = 1

    def get_context_data(self, **kwargs):
        """Переопределние добавляет формсет содержания рассылки"""

        context_data = super().get_context_data(**kwargs)
        content_formset = inlineformset_factory(Content, Video,
                                                form=VideoForm,
                                                extra=self.extra,
                                                can_delete=False)
        if self.request.method == 'POST':
            formset = content_formset(self.request.POST, instance=self.object)
        else:
            formset = content_formset(instance=self.object)

        context_data['formset'] = formset
        return context_data


class IndexView(ListView):
    """Вывод главной страницы"""

    model = Content
    template_name = 'content/index.html'

    def get_queryset(self):
        queryset = super().get_queryset().filter(is_publish=True)[:12]
        return queryset

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        subs_paid = list(self.model.objects.filter(is_publish=True).order_by(
            '-date_update'))
        purchased = list(self.model.objects.filter(is_publish=True).order_by(
            'date_update'))
        context_data['subs_paid'] = subs_paid[:8]
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

        context['video'] = self.object.video.url
        context['title'] = self.object.title
        play_list = list(self.model.objects.all().exclude(pk=self.object.pk))

        # Отображение 10 рандомных записей
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

    success_url = reverse_lazy('content:content_list')

    def form_valid(self, form):
        """Переопределение для добавления владельца и проверки наличия
        обложки видео"""

        formset = self.get_context_data()['formset']

        if formset.is_valid():
            form.instance.owner = self.request.user
            self.object = form.save()
            if not self.object.image:
                task_get_image.delay(pk=self.object.pk)
            formset.instance = self.object
            formset.save()

        return super().form_valid(form)


class ContentUpdateView(UpdateView):
    model = Content
    form_class = ContentUpdateForm

    success_url = reverse_lazy('content:content_list')

    def get_success_url(self):
        """Переопределение для перенаправления после редактирования
        контента"""
        return reverse(
            'content:content_detail',
            args=[self.kwargs.get('pk')]
        )

    # def form_valid(self, form):
    #     """ППереопределение для сохранения формсета"""
    #     formset = self.get_context_data()['formset']
    #
    #     if formset.is_valid():
    #         if not self.object.image:
    #             task_get_image.delay(pk=self.object.pk)
    #         formset.instance = self.object
    #         formset.save()
    #     return super().form_valid(form)


class ContentDeleteView(DeleteView):
    """Представление для удаления контента"""

    model = Content
    success_url = reverse_lazy('content:content_list')

    def form_valid(self, form):
        """Переопределение для удаления файлов связанных с контентом"""
        if self.object.image:
            task_delete_img.delay(path_to=str(self.object.image))
        return super().form_valid(form)
