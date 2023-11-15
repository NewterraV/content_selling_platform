from django import forms
from crispy_forms.helper import FormHelper
from content.src.reg_expressions import RegExpressions

from content.models import Content, Video


class StyleMixin:
    """Класс добавляющий форматирование форм crispy-forms"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()


class ContentForm(StyleMixin, forms.ModelForm):
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

    class Meta:
        model = Content
        fields = ('title', 'description', 'image', 'start_publish',
                  'is_publish', 'is_free', 'is_paid_subs', 'is_src_subs')


class ContentUpdateForm(StyleMixin, forms.ModelForm):
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

    class Meta:
        model = Content
        fields = ('title', 'description', 'image',
                  'is_publish', 'is_free', 'is_paid_subs', 'is_src_subs')


class VideoForm(StyleMixin, forms.ModelForm):
    url = forms.URLField(
        help_text="Ссылка на видео размещенное на видеохостинге YouTube."
                  "Ссылки на другой видеохостинг работать не будут. ",
        widget=forms.TextInput(
            attrs={
                'placeholder': "https://www.youtube.com/..."},
        ),
        max_length=150,
        required=True,
    )

    def save(self, commit=True):
        """Переопределение для добавления video_id во время сохранения"""

        self.instance = super().save(commit=False)
        self.instance.video_id = (
            RegExpressions.get_video_id(self.cleaned_data['url']))
        self.instance.save()
        return self.instance

    class Meta:
        model = Video
        fields = 'url',
