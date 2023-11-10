from django.urls import path
from content.apps import ContentConfig
from content.views import ContentDetailView, ContentListView, \
    ContentCreateView

app_name = ContentConfig.name

urlpatterns = [
    path(
        'detail/<int:pk>/',
        ContentDetailView.as_view(),
        name='content_detail'),
    path('', ContentListView.as_view(), name='content_list'),
    path('create/', ContentCreateView.as_view(), name='content_create'),
]
