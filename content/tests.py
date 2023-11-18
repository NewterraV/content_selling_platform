import datetime
from random import randint
from typing import Any
from unittest.mock import ANY

from content.models import Content, Video
from content.src.api_youtube import YouTubeAPI
from django.test import TestCase

from content.src.reg_expressions import RegExpressions
from subscription.models import PermanentPurchase
from subscription.src.subscription import WorkSubscription, \
    WorkPaidSubscription
from users.models import User


class TestMixin:

    @staticmethod
    def get_user():
        """Метод создает валидного пользователя"""
        user = User.objects.create(
            phone=randint(0000000000, 999999999),
            username=f'test_user{randint(0, 100)}',
            email='test@test.com',
            last_name='Иванов',
            first_name='Иван',
            is_active=True,
            birthday='2010-06-25',
        )
        user.save()
        user.set_password('testtest')
        user.save()
        return user

    def get_auth_user(self):
        """Метод создает и авторизует тестового пользователя"""
        user = self.get_user()
        self.client.login(phone=user.phone, password='testtest')

        return user

    @staticmethod
    def get_content(owner: str, is_publish=True, is_free=True,
                    is_paid_subs=False,
                    is_src_subs=False, is_purchase=False) -> Any:
        """
        Метод создает тестовый экземпляр контента
        """
        content = Content.objects.create(
            owner=owner,
            title='test',
            description='test',
            is_publish=is_publish,
            is_free=is_free,
            is_paid_subs=is_paid_subs,
            is_src_subs=is_src_subs,
            is_purchase=is_purchase,
        )
        content.save()
        video = Video.objects.create(
            content=content,
            url='https://www.youtube.com/watch?v=F3qHa2jaD10',
            video_id='F3qHa2jaD10'
        )
        video.save()
        return content

    def get_create_content(self, title='test',
                           description='test',
                           is_publish=True, is_free=True,
                           is_paid_subs=False,
                           is_src_subs=False, is_purchase=False):
        """Метод создает контент пользователем через запрос"""
        response = self.client.post('/content/create/', {
            'title': title,
            'description': description,
            'is_free': is_free,
            'is_publish': is_publish,
            'is_paid_subs': is_paid_subs,
            'is_src_subs': is_src_subs,
            'is_purchase': is_purchase,
            'video_formset': {
                'url': 'https://www.youtube.com/watch?v=F3qHa2jaD10'
            },
            'product_formset': {
                'price': None,
            }
        })
        return response

    def update_content(self, owner: str, content_pk: str, title='test_update',
                       description='test_update',
                       is_publish=True, is_free=True,
                       is_paid_subs=False,
                       is_src_subs=False, is_purchase=False):
        """Метод обновляет модель через запрос"""
        response = self.client.post(f'/content/{content_pk}/update/', {
            'owner': owner,
            'title': title,
            'description': description,
            'image': '',
            'date_update': datetime.datetime.now(tz=datetime.timezone.utc),
            'start_publish': datetime.datetime.now(tz=datetime.timezone.utc),
            'is_free': is_free,
            'is_publish': is_publish,
            'is_paid_subs': is_paid_subs,
            'is_src_subs': is_src_subs,
            'is_purchase': is_purchase,
            'view_count': 0,
            'product_formset': {
                'price': None,
            }
        })
        return response


class TestContent(TestMixin, TestCase):

    def setUp(self):
        pass

    def test_index(self):
        """Тест представления индекса"""

        response = self.client.get('/')
        self.assertEquals(response.status_code, 200)

        author = self.get_user()
        author_2 = self.get_user()
        # Создаем бесплатные видео
        self.get_content(author)
        self.get_content(author)
        self.get_content(author_2)
        # Создаем видео по платной подписке
        self.get_content(author, is_paid_subs=True, is_free=False)
        self.get_content(author, is_paid_subs=True, is_free=False)
        self.get_content(author_2, is_paid_subs=True, is_free=False)
        # Создаем видео с возможностью разовой покупки
        paid_video = self.get_content(author, is_purchase=True, is_free=False)
        self.get_content(author_2, is_purchase=True, is_free=False)
        self.get_content(author_2, is_purchase=True, is_free=False)
        # Создаем неопубликованные видео
        self.get_content(author, is_publish=False)
        self.get_content(author_2, is_publish=False)
        user = self.get_auth_user()
        WorkSubscription(user).set_subs(author_2.pk)

        response = self.client.get('/')

        self.assertEquals(response.status_code, 200)
        # Так как авторизованный пользователь подписан на author_2, а общее
        # количество видео на платформе 12, то он получит все бесплатные видео
        # автора-1 и все видео кроме видео по платной подписке автора-2,
        # то-есть 6
        self.assertEquals(len(response.context_data['object_list']), 6)

        # Добавим платную подписку на автора-2
        WorkPaidSubscription(user).set_subs(author_2.pk)
        response = self.client.get('/')
        # Общий контекст не поменяется
        self.assertEquals(len(response.context_data['object_list']), 6)
        # А в контексте с платными подписками появится 4 видео, это все
        # опубликованные видео автора-2
        self.assertEquals(len(response.context_data['subs_paid_content']),
                          4)

        # Добавим 1 видео автора-1 в список купленных пользователем
        purchase = PermanentPurchase.objects.create(
            owner=user,
            content=paid_video
        )
        purchase.save()
        response = self.client.get('/')
        # Предыдущий контекст не поменяется
        self.assertEquals(len(response.context_data['object_list']), 6)
        self.assertEquals(len(response.context_data['subs_paid_content']),
                          4)
        # А в списке купленных автором видео появится 1 видео автора 1
        self.assertEquals(len(response.context_data['purchased']), 1)

    def test_content_list(self):
        """Тест представления списка контента"""

        response = self.client.get('/content/')

        self.assertEquals(response.status_code, 302)

        user = self.get_auth_user()
        for i in range(4):
            self.get_content(user)

        response = self.client.get('/content/')

        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.context_data['object_list']),
                          4)

    def test_content_detail(self):
        """Тест представления детальной информации о контенте"""

        user = self.get_auth_user()
        content = self.get_content(owner=user)

        response = self.client.get(f'/content/{content.pk}/detail/')

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context_data, {
            'object': ANY,
            'content': ANY,
            'view': ANY,
            'subs': {
                'subs': False,
                'paid_subs': False,
                'src_subs': False,
                'purchase': ANY
            },
            'sub': {
                'subs_count': 0,
                'paid_subs_price': None,
                'paid_subs_currency': None,
                'paid_subs_pk': None
            },
            'video': 'F3qHa2jaD10',
            'title': 'test',
            'play_list': []
        })

    def test_create_view(self):
        """Тест представления создания контента"""

        # Тест создания контента неавторизованным пользователем

        response = self.client.post('/content/create/')
        content = Content.objects.count()

        self.assertEquals(response.status_code, 302)
        self.assertEquals(content, 0)

        # тест создания авторизованным пользователем с валидными данными

        self.get_auth_user()
        self.get_create_content()
        content = Content.objects.get()

        self.assertEquals(response.status_code, 302)
        self.assertEquals(content.__dict__, {
            '_state': ANY,
            'id': ANY, 'owner_id': ANY, 'title': 'test',
            'description': 'test',
            'image': ANY, 'date_update': ANY, 'start_publish': ANY,
            'is_publish': True, 'is_free': True, 'is_paid_subs': False,
            'is_src_subs': False, 'is_purchase': False, 'view_count': 0})

        # Тест валидации
        Content.objects.all().delete()
        self.get_create_content(is_src_subs=True)
        content = Content.objects.count()
        self.assertEquals(response.status_code, 302)
        self.assertEquals(content, 0)

        self.get_create_content(is_purchase=True)
        content = Content.objects.count()
        self.assertEquals(response.status_code, 302)
        self.assertEquals(content, 0)

        self.get_create_content(is_paid_subs=True)
        content = Content.objects.count()
        self.assertEquals(response.status_code, 302)
        self.assertEquals(content, 0)

    def test_update_view(self):
        """Тест представления обновления контента"""
        user = self.get_user()
        content = self.get_content(user)

        # Тест неавторизованного пользователя
        response = self.update_content(user.pk, content.pk)
        self.assertEquals(response.status_code, 302)
        self.assertEquals(content.title, 'test')
        Content.objects.all().delete()

        # Тест валидного обновления
        user = self.get_auth_user()
        self.get_create_content()
        content = Content.objects.get()
        response = self.update_content(owner=user.pk, content_pk=content.pk)
        content = Content.objects.get()
        self.assertEquals(response.status_code, 302)
        self.assertEquals(content.__dict__, {
            '_state': ANY,
            'id': ANY, 'owner_id': ANY, 'title': 'test_update',
            'description': 'test_update',
            'image': '', 'date_update': ANY, 'start_publish': ANY,
            'is_publish': True, 'is_free': True, 'is_paid_subs': False,
            'is_src_subs': False, 'is_purchase': False, 'view_count': 0})

        response = self.update_content(owner=user.pk, content_pk=content.pk,
                                       is_paid_subs=True)
        content = Content.objects.get()
        self.assertEquals(response.status_code, 200)
        self.assertEquals(content.is_paid_subs, False)

    def test_content_delete(self):
        """Тест представления удаления контента"""

        # Тест неавторизованного удаления
        user = self.get_user()
        content = self.get_content(user)
        response = self.client.post(f'/content/{content.pk}/delete/')
        content_count = Content.objects.count()
        self.assertEquals(response.status_code, 302)
        self.assertEquals(content_count, 1)

        # Тест удаления не владельцем
        self.get_auth_user()
        response = self.client.post(f'/content/{content.pk}/delete/')
        content_count = Content.objects.count()
        self.assertEquals(response.status_code, 404)
        self.assertEquals(content_count, 1)

        # тест валидного удаления
        user = self.get_auth_user()
        Content.objects.all().delete()
        Video.objects.all().delete()
        content = self.get_content(user)
        response = self.client.post(f'/content/{content.pk}/delete/')
        content_count = Content.objects.count()
        video_count = Video.objects.count()
        self.assertEquals(response.status_code, 302)
        self.assertEquals(content_count, 0)
        self.assertEquals(video_count, 0)


class TestYouTubeAPI(TestCase):

    def test_get_video_cover(self):
        """Тест функции получения ссылки на картинку"""

        response = YouTubeAPI().get_video_cover(
            video_id='F3qHa2jaD10')
        self.assertEquals(response,
                          "https://i.ytimg.com/vi/F3qHa2jaD10"
                          "/sddefault.jpg")


class TestRegExpressions(TestCase):

    def test_get_video_id(self):
        """Тест функции получения id видео из ссылки"""

        response = [RegExpressions().get_video_id(
            'https://www.youtube.com/watch?v=F3qHa2jaD10'),
            RegExpressions().get_video_id(
                'https://youtu.be/F3qHa2jaD10?si=gXBnLBqvipK1fhBm'),
        ]

        self.assertEquals(response[0], 'F3qHa2jaD10')
        self.assertEquals(response[1], 'F3qHa2jaD10')
