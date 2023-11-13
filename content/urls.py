from django.urls import path
from content.apps import ContentConfig
from content.views import ContentDetailView, ContentListView, \
    ContentCreateView, ContentUpdateView, IndexView

app_name = ContentConfig.name

urlpatterns = [
    path(
        'content/<int:pk>/detail/',
        ContentDetailView.as_view(),
        name='content_detail'),
    path('content/', ContentListView.as_view(), name='content_list'),
    path('content/create/', ContentCreateView.as_view(),
         name='content_create'),
    path('content/<int:pk>/update/', ContentUpdateView.as_view(),
         name='content_update'),
    path('', IndexView.as_view(), name='index')
]
