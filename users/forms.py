from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, \
    UsernameField, UserChangeForm
from django import forms

from content.forms import StyleMixin
from users.models import User, Verify


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
        label="Номер",
        widget=forms.TextInput(
            attrs={'class': '"col-form-label"',
                   'type': 'text',
                   'id': 'addon-wrapping',
                   'placeholder': '10 цифр без +7'},
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
                   'placeholder': '10 цифр без +7',
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


class VerifyForm(forms.ModelForm):

    user_code = forms.CharField(
        label="",
        widget=forms.TextInput(
            attrs={'class': 'form-control',
                   'type': 'text',
                   'id': 'addon-wrapping',
                   'placeholder': '0000'},
        ),
        help_text='Сейчас вам поступит звонок, введите последние 4 цифры '
                  'номера звонящего',
        max_length=4,
        required=True
    )

    class Meta:
        model = Verify
        fields = 'user_code',

    def clean(self):
        """Метод проверяет правильность введенного пользователем кода"""

        cleaned_data = super().clean()
        user_code = cleaned_data.get('user_code')
        if int(user_code) != self.instance.verify_code:
            raise forms.ValidationError('Неверный код')

        return cleaned_data
