from django.urls import path
from users.apps import UsersConfig
from users.views import UserRegisterView, LoginView, LogoutView, \
    UserUpdateView

app_name = UsersConfig.name

urlpatterns = [
    path('create/', UserRegisterView.as_view(), name='user_create'),
    path('update/', UserUpdateView.as_view(), name='user_update'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
