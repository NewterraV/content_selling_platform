from django.urls import path
from content.apps import ContentConfig
from content.views import ContentDetailView


app_name = ContentConfig.name

urlpatterns = [
    path(
        'detail/<int:pk>/',
        ContentDetailView.as_view(),
        name='content_detail'),
]
