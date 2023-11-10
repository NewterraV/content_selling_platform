from django.forms import inlineformset_factory
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    ListView,
    DetailView,
    DeleteView,
    CreateView,
    UpdateView
)

from content.forms import VideoForm, ContentForm
from content.models import Content, Video
from random import sample


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
        # context['owner'] = self.object.owner
        play_list = list(self.model.objects.all().exclude(pk=self.object.pk))


        # Отображение 10 рандомных записей
        context['play_list'] = sample(play_list, 10) if len(
            play_list) > 10 else play_list

        return context


class ContentListView(ListView):
    """Контроллер для отображения списка контента"""

    model = Content


class ContentCreateView(ContentFormsetMixin, CreateView):

    model = Content
    form_class = ContentForm

    success_url = reverse_lazy('content:content_list')

    def form_valid(self, form):
        formset = self.get_context_data()['formset']

        if formset.is_valid():
            self.object = form.save()
            # self.object.owner = self.request.user
            # self.object.save()
            formset.instance = self.object
            formset.save()
        return super().form_valid(form)


class ContentUpdateView(ContentFormsetMixin, UpdateView):

    model = Content
    form_class = ContentForm

    success_url = reverse_lazy('content:content_list')

    def get_success_url(self):
        return reverse(
            'content:content_detail',
            args=[self.kwargs.get('pk')]
        )

    def form_valid(self, form):
        formset = self.get_context_data()['formset']

        if formset.is_valid():
            formset.instance = self.object
            formset.save()
        return super().form_valid(form)
