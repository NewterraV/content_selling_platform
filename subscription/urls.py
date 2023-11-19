from subscription.apps import SubscriptionConfig
from django.urls import path

from subscription.views import subscribe

app_name = SubscriptionConfig.name

urlpatterns = [
    path('<int:pk>/subscribe/', subscribe, name='subscribe'),
]
