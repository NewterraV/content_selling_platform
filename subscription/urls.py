from subscription.apps import SubscriptionConfig
from django.urls import path

from subscription.views import subscribe, subs_status

app_name = SubscriptionConfig.name

urlpatterns = [
    path('<int:pk>/subscribe/', subscribe, name='subscribe'),
    path('<int:pk>/status/', subs_status, name='subs_status'),
]
