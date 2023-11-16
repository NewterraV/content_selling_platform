from django import forms

from product.models import Product
from product.tasks import task_create_product


class ProductForm(forms.ModelForm):
    price = forms.IntegerField(
        label="Цена пожизненной покупки доступа к контенту",
        widget=forms.TextInput(
            attrs={
                'placeholder': "100"},
        ),
        help_text='Введите цену на покупку контента. '
                  'Цена должна быть целочисленным '
                  'значением',
        required=False,
    )

    class Meta:
        model = Product
        fields = ('price', 'currency')


class UserProductForm(forms.ModelForm):
    price = forms.IntegerField(
        label="Цена подписки на пользователя",
        widget=forms.TextInput(
            attrs={
                'placeholder': "100"},
        ),
        help_text='Введите цену на подписку. '
                  'Если вы не планируете размещать платный контент, '
                  'оставьте поле пустым. Цену на подписку можно будет '
                  'изменить после регистрации в разделе редактирования '
                  'профиля',
        required=False,
    )

    def save(self, commit=True):
        if self.instance.price:
            self.instance.save()
            task_create_product.delay(self.instance.pk)
        return self.instance

    class Meta:
        model = Product
        fields = ('price', 'currency')

