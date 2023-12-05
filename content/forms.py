import re

from django import forms
from crispy_forms.helper import FormHelper
from content.src.reg_expressions import RegExpressions

from content.models import Content, Video
from product.models import Product


class StyleMixin:
    """Класс добавляющий форматирование форм crispy-forms"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()


class ValidateMixin:
    """Класс добавляющий методы валидации формам связанным с контентом"""

    def clean_is_paid_subs(self):
        """Метод валидации поля платной подписки"""
        cleaned_data = self.cleaned_data.get('is_paid_subs')
        user_paid = Product.objects.filter(user=self.user)
        if cleaned_data and not user_paid:
            raise forms.ValidationError('Невозможно создать видео по подписке'
                                        ' так как вы не указали цену подписки'
                                        ' на пользователя при регистрации.'
                                        'Указать цену можно на странице '
                                        'редактирования пользователя')
        return cleaned_data

    def clean(self):
        """Переопределение для проверки указания доступности контента"""

        cleaned_data = super().clean()
        is_free = self.cleaned_data.get('is_free')
        is_paid_subs = self.cleaned_data.get('is_paid_subs')
        is_src_subs = self.cleaned_data.get('is_src_subs')
        is_purchase = self.cleaned_data.get('is_purchase')

        if True not in [is_free, is_paid_subs, is_src_subs, is_purchase]:
            raise forms.ValidationError('Укажите минимум один параметр '
                                        'доступности видео: бесплатно, по '
                                        'подписке, по подписке на сервис, '
                                        'по разовой покупке')
        if is_free and is_paid_subs:
            raise forms.ValidationError('Видео не может быть одновременно '
                                        'бесплатным и по подписке на '
                                        'пользователя')
        if is_free and is_src_subs:
            raise forms.ValidationError('Видео не может быть одновременно '
                                        'бесплатным и по подписке на сервис')
        if is_free and is_purchase:
            raise forms.ValidationError('Видео не может быть одновременно '
                                        'бесплатным и доступным к покупке в'
                                        ' коллекцию')
        return cleaned_data


class ContentForm(StyleMixin, ValidateMixin, forms.ModelForm):
    """Класс описывающий форму для создания нового экземпляра контента"""

    title = forms.CharField(
        label="Название",
        help_text="Введите название записи. Ограничение 150 символов.",
        widget=forms.TextInput(
            attrs={
                'placeholder': "Лучшее название на планете..."},
        ),
        max_length=100,
        required=True,
    )
    description = forms.CharField(
        label="Описание",
        help_text="Введите название записи. Ограничение 150 символов.",
        widget=forms.Textarea(
            attrs={
                'placeholder': "Лучшее Описание на планете..."},
        ),
        required=True,
    )
    image = forms.ImageField(
        label="Изображение",
        help_text="Используйте изображение с соотношением сторон 16 на 9. "
                  "Данное изображение будет использовано как заставка к "
                  "видео . Если поле оставить пустым, то будет использовано "
                  "превью видео из YouTube.",
        required=False,
    )

    is_free = forms.BooleanField(

        label="Бесплатный контент",
        help_text="Установите галочку если контент будет доступен всем "
                  "пользователям без какой-либо оплаты."
                  "Если активно, то будет игнорироваться поле 'цена'",
        required=False,
    )

    start_publish = forms.DateTimeField(
        label="Время публикации",
        widget=forms.DateTimeInput(
            attrs={'type': 'datetime-local'},
        ),
        help_text="Укажите дату и время в которое автоматически будет "
                  "опубликована запись",
        required=False
    )

    is_publish = forms.BooleanField(

        label="Опубликовать сразу",
        help_text="Если активно, то запись будет опубликована "
                  "сразу после создания",
        required=False,
    )

    is_paid_subs = forms.BooleanField(

        label="Контент в подписке на пользователя",
        help_text='Установите галочку если контент будет доступен всем '
                  'пользователям оплатившим подписку на вас',
        required=False,
    )

    is_src_subs = forms.BooleanField(

        label="Контент в подписке на сервис",
        help_text='Установите галочку если контент будет доступен всем '
                  'пользователям оплатившим подписку на сервис. Вы будете'
                  'получать ежемесячное роялти в зависимости от просмотров',
        required=False,
    )

    is_purchase = forms.BooleanField(

        label="Контент доступен для покупки в коллекцию",
        help_text='Установите галочку если контент будет доступен для '
                  'единовременной покупки. Пользователь получит доступ к '
                  'контенту навсегда, а вы разовую единовременную оплату.'
                  'Если поле активно, необходимо казать цену для разовой'
                  ' покупки',
        required=False,
    )

    def __init__(self, *args, **kwargs):
        """Переопределение для фильтрации содержимого поля clients"""

        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    class Meta:
        model = Content
        fields = ('title', 'description', 'image', 'start_publish',
                  'is_publish', 'is_free', 'is_paid_subs', 'is_src_subs',
                  'is_purchase')


class ContentUpdateForm(StyleMixin, ValidateMixin, forms.ModelForm):
    """Класс описывающий форму для обновления экземпляра контента"""

    title = forms.CharField(
        label="Название",
        help_text="Введите название записи. Ограничение 150 символов.",
        widget=forms.TextInput(
            attrs={
                'placeholder': "Лучшее название на планете..."},
        ),
        max_length=100,
        required=True,
    )

    description = forms.CharField(
        label="Описание",
        help_text="Введите название записи. Ограничение 150 символов.",
        widget=forms.TextInput(
            attrs={
                'placeholder': "Лучшее Описание на планете..."},
        ),
        required=True,
    )

    image = forms.ImageField(
        label="Изображение",
        help_text="Используйте изображение с соотношением сторон 16 на 9. "
                  "Данное изображение будет использовано как заставка к "
                  "видео . Если поле оставить пустым, то будет использовано "
                  "превью видео из YouTube.",
        required=False,
    )

    is_free = forms.BooleanField(

        label="Бесплатный контент",
        help_text="Установите галочку если контент будет доступен всем "
                  "пользователям без какой-либо оплаты."
                  "Если активно, то будет игнорироваться поле 'цена'",
        required=False,
    )

    is_paid_subs = forms.BooleanField(

        label="Контент в подписке на пользователя",
        help_text='Установите галочку если контент будет доступен всем '
                  'пользователям оплатившим подписку на вас',
        required=False,
    )

    is_src_subs = forms.BooleanField(

        label="Контент в подписке на сервис",
        help_text='Установите галочку если контент будет доступен всем '
                  'пользователям оплатившим подписку на сервис. Вы будете'
                  'получать ежемесячное роялти в зависимости от просмотров',
        required=False,
    )

    is_purchase = forms.BooleanField(

        label="Контент доступен для покупки в коллекцию",
        help_text='Установите галочку если контент будет доступен для '
                  'единовременной покупки. Пользователь получит доступ к '
                  'контенту навсегда, а вы разовую единовременную оплату.'
                  'Если поле активно, необходимо казать цену для разовой'
                  ' покупки',
        required=False,
    )

    class Meta:
        model = Content
        fields = ('title', 'description', 'image',
                  'is_free', 'is_paid_subs', 'is_src_subs', 'is_purchase')

    def __init__(self, *args, **kwargs):
        """Переопределение для фильтрации содержимого поля clients"""

        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)


class VideoForm(StyleMixin, forms.ModelForm):
    """Форма описывающая видео"""
    url = forms.URLField(
        help_text="Ссылка на видео размещенное на видеохостинге YouTube."
                  "Ссылки на другой видеохостинг работать не будут. ",
        widget=forms.TextInput(
            attrs={
                'placeholder': "https://www.youtube.com/..."},
        ),
        max_length=150,
    )

    def save(self, commit=True):
        """Переопределение для добавления video_id во время сохранения"""

        self.instance = super().save(commit=False)
        self.instance.video_id = (
            RegExpressions.get_video_id(self.cleaned_data['url']))
        self.instance.save()
        return self.instance

    def clean_url(self):
        """Метод валидации поля платной подписки"""
        cleaned_data = self.cleaned_data.get('url')
        if cleaned_data:
            if 'youtu' not in cleaned_data:
                raise forms.ValidationError(
                    'Допускается использование видео только'
                    ' с хостинга "YouTube"')

            return cleaned_data

        else:
            raise forms.ValidationError(
                'Кажется вы забыли указать ссылку на видео')

    class Meta:
        model = Video
        fields = 'url',
