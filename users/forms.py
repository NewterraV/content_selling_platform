from crispy_forms.helper import FormHelper
from crispy_forms.layout import MultiWidgetField, Field, Layout, Div
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, \
    UsernameField, UserChangeForm
from django import forms

from content.forms import StyleMixin
from users.models import User


class RegisterForm(StyleMixin, UserCreationForm):
    """Форма для регистрации нового пользователя"""

    birthday = forms.DateField(
        label="Дата рождения",
        widget=forms.DateInput(
            attrs={'type': 'date'},
        ),
        required=True
    )

    phone = forms.CharField(
        label="Телефон",
        widget=forms.TextInput(
            attrs={'class': 'form-control',
                   'type': 'text',
                   'id': 'addon-wrapping'},
        ),
        max_length=10,
        required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = User
        fields = (
            'phone',
            'password1',
            'password2',
            'email',
            'username',
            'first_name',
            'last_name',
            'birthday',
            'avatar',
        )


class UserUpdateForm(StyleMixin, UserChangeForm):
    """Форма для обновления профиля пользователя"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].widget = forms.HiddenInput()

    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'avatar',
        )


class LoginForm(StyleMixin, AuthenticationForm):
    username = UsernameField(
        label='',
        widget=forms.TextInput(
            attrs={"autofocus": True,
                   'placeholder': '9397190195',
                   'type': 'phone'
                   }))
    password = forms.CharField(
        label='',
        strip=False,
        widget=forms.PasswordInput(
            attrs={"autocomplete": "current-password",
                   'placeholder': 'Пароль'}
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
