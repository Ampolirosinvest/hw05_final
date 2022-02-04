from django.test import TestCase, Client
from django.db import models

from ..models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        # Создаем неавторизированный клиет
        self.guest_client = Client()
        # Создаем авторизованный клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        group = PostModelTest.group
        models_all = {
            post.text[:15]: str(post),
            group.title: str(group)
        }
        for expected_object_name, strpost in models_all.items():
            with self.subTest(expected_object_name=expected_object_name):
                self.assertEqual(expected_object_name, strpost)

    def test_poley(self):
        """Проверяем поля в модели cоответсвуют ожидаемым."""
        models_all = {
            Post.text: models.fields.TextField,
            Post.author: models.ForeignKey,
            Group.title: models.fields.CharField,
            Group.slug: models.fields.SlugField,
            Group.description: models.fields.TextField,
        }
        for object_name, models_typy in models_all.items():
            with self.subTest(object_name=object_name):
                self.assertIsInstance(type(object_name), type(models_typy))
