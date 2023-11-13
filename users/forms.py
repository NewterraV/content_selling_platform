from crispy_forms.helper import FormHelper
from crispy_forms.layout import MultiWidgetField, Field, Layout, Div
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
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
        self.helper.label_class = 'form-floating'

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


class LoginForm(StyleMixin, AuthenticationForm):
    pass
