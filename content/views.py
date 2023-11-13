from django.forms import inlineformset_factory
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    ListView,
    DetailView,
    DeleteView,
    CreateView,
    UpdateView,
    View
)

from content.forms import VideoForm, ContentForm
from content.models import Content, Video
from random import sample

from content.tasks import task_get_image


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


def index(request):
    """Метод представления главной страницы"""
    context = {
        'title': 'Домашняя страница'
    }

    return render(request, 'content/index.html', context)


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


class ContentListView(ListView):
    """Контроллер для отображения списка контента"""

    model = Content
    extra_context = {'title': 'Видео'}


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


class ContentUpdateView(ContentFormsetMixin, UpdateView):

    model = Content
    form_class = ContentForm

    success_url = reverse_lazy('content:content_list')

    def get_success_url(self):
        """Переопределение для перенаправления после редактирования
        контента"""
        return reverse(
            'content:content_detail',
            args=[self.kwargs.get('pk')]
        )

    def form_valid(self, form):
        """ППереопределение для сохранения формсета"""
        formset = self.get_context_data()['formset']

        if formset.is_valid():
            if not self.object.image:
                task_get_image.delay(pk=self.object.pk)
            formset.instance = self.object
            formset.save()
        return super().form_valid(form)
