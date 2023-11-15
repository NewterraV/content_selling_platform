from django import forms

from product.models import Product


class ProductForm(forms.ModelForm):
    price = forms.IntegerField(
        label="Цена",
        widget=forms.TextInput(
            attrs={
                'placeholder': "100"},
        ),
        help_text='Введите цену на продукт .Цена должна быть целочисленным '
                  'значением',
        required=False,
    )

    class Meta:
        model = Product
        fields = ('price', 'currency')
