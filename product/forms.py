from django import forms

from product.models import Product
from product.tasks import task_create_product, task_delete_product, \
    task_update_product


class ProductFormMixin:
    """Класс для обновления методов форм продукта"""

    def save(self, commit=True):
        """Переопределение для обновления продукта в зависимости от
        исходного состояния"""
        if Product.objects.filter(pk=self.instance.pk).first():
            if self.instance.price:
                self.instance.save()
                task_update_product.delay(self.instance.pk)
                return self.instance
            else:
                task_delete_product.delay(self.instance.stripe_id)
                self.instance.delete()
                return self.instance

        if self.instance.price:
            self.instance.save()
            task_create_product.delay(self.instance.pk)
        return self.instance


class ProductForm(ProductFormMixin, forms.ModelForm):
    price = forms.IntegerField(
        label="Цена пожизненной покупки доступа к контенту",
        widget=forms.TextInput(
            attrs={
                'placeholder': "49"},
        ),
        initial='49',
        help_text='Введите цену на покупку контента. '
                  'Цена должна быть целочисленным '
                  'значением',
        required=False,
    )

    # def clean(self):
    #     cleaned_data = super().clean()
    #     price = self.cleaned_data.get('price')
    #     if price is None:
    #         raise forms.ValidationError('поле цена не может быть пустым если '
    #                                     'указана возможность покупки в '
    #                                     'коллекцию.')
    #     if price <= 0:
    #         raise forms.ValidationError('Цена разовой покупки должна быть'
    #                                     ' больше нуля')
    #     return cleaned_data
    #
    # def clean_price(self):
    #     """Метод валидации поля платной подписки"""
    #     cleaned_data = self.cleaned_data.get('price')
    #     if cleaned_data is None:
    #         raise forms.ValidationError('поле цена не может быть пустым если '
    #                                     'указана возможность покупки в '
    #                                     'коллекцию.')
    #     if cleaned_data <= 0:
    #         raise forms.ValidationError('Цена должна быть больше 0')
    #     return cleaned_data

    class Meta:
        model = Product
        fields = ('price', 'currency')


class UserProductForm(ProductFormMixin, forms.ModelForm):
    price = forms.IntegerField(
        label="Цена подписки на пользователя",
        widget=forms.TextInput(
            attrs={
                'placeholder': "99"},
        ),
        help_text='Введите цену на подписку. '
                  'Если вы не планируете размещать платный контент, '
                  'оставьте поле пустым. Цену на подписку можно будет '
                  'изменить после регистрации в разделе редактирования '
                  'профиля',
        required=False,
    )

    class Meta:
        model = Product
        fields = ('price', 'currency')

