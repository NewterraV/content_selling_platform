from django.test import TestCase

from content.tests import TestMixin
from product.models import Product
from product.src.Payment import UserProduct


class TestProduct(TestMixin, TestCase):
    """Тест-кейс приложения product"""

    def test_user_product_class(self):
        """Тест получения id продукта и его изменения на сервисе Stripe"""
        user = self.get_auth_user()

        example = Product.objects.create(
            user=user,
            price=2,
            currency='usd'
        )
        example.save()

        product = UserProduct(example.pk)
        product.create_ids_product()

        product_example = Product.objects.get()
        self.assertIsNotNone(product_example.stripe_id)
        self.assertIsNotNone(product_example.price_stripe_id)
        stripe_id = product_example.stripe_id
        price_stripe_id = product_example.price_stripe_id

        product.update_product()

        product_example = Product.objects.get()
        self.assertNotEquals(product_example.stripe_id, stripe_id)
        self.assertNotEquals(product_example.price_stripe_id, price_stripe_id)
