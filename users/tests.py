from django.test import TestCase

from content.models import Content
from content.tests import TestMixin


class TestUser(TestMixin, TestCase):
    """Тест-кейс приложения users"""

    def test_user_detail(self):
        """Тест представления страницы с детальной информацией
         о пользователе"""

        # Подготовка тестовых данных
        author = self.get_user()
        for i in range(4):
            self.get_content(author)

        user = self.get_auth_user()
        for i in range(10):
            self.get_content(user)

        author_content_count = Content.objects.filter(owner=author.pk).count()
        user_content_count = Content.objects.filter(owner=user.pk).count()

        response = self.client.get(
            f'/users/{author.pk}/detail/'
        )

        # Проверка вывода видео пользователя в контекст
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.context_data['content_list']),
                          author_content_count)

        response = self.client.get(
            f'/users/{user.pk}/detail/'
        )
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.context_data['content_list']),
                          user_content_count)
