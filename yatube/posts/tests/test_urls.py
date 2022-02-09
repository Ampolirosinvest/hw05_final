from http.client import OK, FOUND, NOT_FOUND
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from posts.models import Post, Group

User = get_user_model()


class StaticURLTestsGuest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='1',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        # Устанавливаем данные для тестирования
        # Создаём экземпляр клиента. Он неавторизован.
        self.guest_client = Client()

    def test_guest_client(self):
        """Проверка работоспособности общих страниц yatube"""
        # Отправляем запрос через client,
        # созданный в setUp()
        # расписал в списке все рабочие страницы доступные без авторизации
        # Можно поменять местами ключ значение и условие ниже
        # и добавить все в один список
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': '/group/1/',
            'posts/profile.html': '/profile/auth/',
            'posts/post_detail.html': '/posts/1/',
        }
        # прошелся по словарю, у каждой страницы проверил статус 200(OK)
        # и шаблон.
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, OK)
                self.assertTemplateUsed(response, template)

    def test_edit_create_pages_guest(self):
        """Страницы редактирования posts/<post_id>/edit
        и /create/ недоступны неавторизированным пользователям 302(FOUND)"""
        templates_url_names = {
            '/posts/1/edit/': FOUND,
            '/create/': FOUND,
            '/posts/1/comment/': FOUND,  # добавил
        }
        # прошелся по словарю, у каждой страницы проверил статус 302(FOUND).
        for address, code in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, code)

    def ttest_unexisting_page(self):
        """Страница unexisting_page проверка на ее отсутсвие 404(NOT_FOUND)"""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, NOT_FOUND)


class StaticURLTestsAuthorized(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='1',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)

    def test_edit_create_pages(self):
        """Страницы редактирования posts/<post_id>/edit
        и /create/ и /comment/ доступны авторизированным пользователям"""
        templates_url_names = {
            '/posts/1/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
            '/posts/1/comment/': 'posts/comments.html',  # добавил
        }
        # прошелся по словарю, у каждой страницы проверил статус 200(OK)
        # и шаблон.
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, OK)
                self.assertTemplateUsed(response, template)
