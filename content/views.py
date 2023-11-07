from django.views.generic import (
    ListView,
    DetailView,
    DeleteView,
    CreateView,
    UpdateView
)
from content.models import Content
from random import sample


class ContentDetailView(DetailView):
    model = Content

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['video'] = self.object.video.url
        context['title'] = self.object.title
        # context['owner'] = self.object.owner
        play_list = list(self.model.objects.all().exclude(pk=self.object.pk))
        context['play_list'] = sample(play_list, 10) if len(
            play_list) > 10 else play_list
        return context
