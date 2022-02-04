from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from django.core.cache import cache
from posts.models import Post, Group, Follow

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='1',
            description='Тестовое описание',
        )
        cls.group2 = Group.objects.create(
            title='Тестовая группа2',
            slug='2',
            description='Тестовое описание2',
        )
        for i in range(13):
            cls.post = Post.objects.create(
                author=cls.user,
                text='Тестовый пост',
                group=cls.group
            )

    def setUp(self):
        # Создаем неавторизированный клиет
        self.guest_client = Client()
        # Создаем авторизованный клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.index_revers = reverse('posts:index')
        self.group_revers = reverse('posts:group_posts', kwargs={'slug': '1'})
        self.profile_revers = reverse('posts:profile',
                                      kwargs={'username': 'auth'})
        self.post_detail_revers = reverse('posts:post_detail',
                                          kwargs={'post_id': '1'})
        self.post_edit_revers = reverse('posts:post_edit',
                                        kwargs={'post_id': '1'})
        self.post_create_revers = reverse('posts:post_create')
        self.index_template = 'posts/index.html'
        self.group_template = 'posts/group_list.html'
        self.profile_template = 'posts/profile.html'
        self.post_detail_template = 'posts/post_detail.html'
        self.post_edit_create_template = 'posts/create_post.html'

    # Проверка шаблонов
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары reverse(name): имя_шаблона"
        templates_pages_names = {
            self.index_revers: self.index_template,
            self.group_revers: self.group_template,
            self.profile_revers: self.profile_template,
            self.post_detail_revers: self.post_detail_template,
            self.post_edit_revers: self.post_edit_create_template,
            self.post_create_revers: self.post_edit_create_template,
        }
        # Проверяем, что при обращении к name вызывается соответ. HTML-шаблон
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    # Проверяем контекст в шаблонах
    def test_create_and_edit_page_show_correct_context(self):
        """Шаблоны create и edit сформирован с правильным контекстом."""
        response_all = [
            self.authorized_client.get(self.post_create_revers),
            self.authorized_client.get(self.post_edit_revers),
        ]
        # Словарь ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        for response in response_all:
            form_fields = {
                'text': forms.fields.CharField,
                'group': forms.ModelChoiceField,
            }

        # Проверяем, что типы полей формы в context соответствуют ожиданиям
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context.get('form').fields.get(value)
                    # Проверяет, что поле формы является экземпляром
                    # указанного класса
                    self.assertIsInstance(form_field, expected)

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.post_detail_revers)
        self.assertEqual(response.context.get('post').text, self.post.text)
        self.assertEqual(response.context.get('post').author, self.user)
        self.assertEqual(response.context.get('post').id, 1)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.index_revers)
        first_object = response.context['page_obj'][0]
        post_text_one = first_object.text
        self.assertEqual(post_text_one, self.post.text)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.profile_revers)
        first_object = response.context['page_obj'][0]
        post_text_one = first_object.text
        post_author_one = first_object.author
        self.assertEqual(post_text_one, self.post.text)
        self.assertEqual(post_author_one, self.user)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.group_revers)
        self.assertEqual(response.context.get('group').title,
                         self.group.title)
        self.assertEqual(response.context.get('group').slug,
                         self.group.slug)
        self.assertEqual(response.context.get('group').description,
                         self.group.description)
        self.assertEqual(response.context.get('group').id, 1)

    # Проверка паджинатора страниц index, group и profile
    def test_one_two_page_contains_ten_records_all(self):
        """Проверка паджинатора страницы index 1 и 2"""
        paginator = {
            self.client.get(self.index_revers):
                self.client.get(self.index_revers + '?page=2'),
            self.client.get(self.group_revers):
                self.client.get(self.group_revers + '?page=2'),
            self.client.get(self.profile_revers):
                self.client.get(self.profile_revers + '?page=2'),
        }
        for one_page, two_page in paginator.items():
            with self.subTest(one_page=one_page):
                response_one_page = one_page
                response_two_page = two_page
                # Проверка: количество постов на первой странице равно 10.
                self.assertEqual(len(
                    response_one_page.context['page_obj']), 10)
                # Проверка: количество постов на первой странице равно 3.
                self.assertEqual(len(
                    response_two_page.context['page_obj']), 3)

    def test_post_appears_on_pages(self):
        """Проверка постов на index и profile и group
        на наличие при публикации"""

        urls = [
            self.index_revers,
            self.group_revers,
            self.profile_revers,
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                first_object = response.context['page_obj'][0]
                post_text = first_object.text
                post_group = first_object.group.title
                self.assertEqual(post_text, self.post.text)
                self.assertEqual(post_group, self.post.group.title)


class CacheTests(TestCase):
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
            group=cls.group
        )

    def setUp(self):
        # Создаем авторизованный клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_cache_index(self):
        """Проверка хранения и очищения кэша для index."""
        response = self.authorized_client.get(reverse('posts:index'))
        posts = response.content
        Post.objects.create(
            text='Тестовый пост',
            author=self.user,
        )
        response_old = self.authorized_client.get(reverse('posts:index'))
        old_posts = response_old.content
        self.assertEqual(old_posts, posts, 'Не возвращает кэш страницу.')
        cache.clear()
        response_new = self.authorized_client.get(reverse('posts:index'))
        new_posts = response_new.content
        self.assertNotEqual(old_posts, new_posts, 'Кеш не сбрасывается.')


class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user_follower = User.objects.create_user(
            username='auth_follower'
        )
        cls.user_unfollower = User.objects.create_user(
            username='auth_unfollower'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='1',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )

    def setUp(self):
        # Создаем неавторизированный клиент
        self.guest_client = Client()
        # Создаем авторизованный клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        # Создаем авторизироанный клиент follower
        self.authorized_user_follower_client = Client()
        self.authorized_user_follower_client.force_login(
            self.user_follower
        )
        # Создаем авторизироанный клиент unfollower
        self.authorized_user_unfollower_client = Client()
        self.authorized_user_unfollower_client.force_login(
            self.user_unfollower
        )

    def test_auth_follow(self):
        """Тест - подписка на автора."""
        client = self.authorized_user_unfollower_client
        user = self.user_unfollower
        author = self.user
        client.get(reverse('posts:profile_follow',
                   kwargs={'username': 'auth'}))
        follower = Follow.objects.filter(
            user=user,
            author=author
        ).exists()
        self.assertTrue(follower, 'Подписка не работает')

    def test_auth_unfollow(self):
        """Тест - отписка от автора."""
        client = self.authorized_user_unfollower_client
        user = self.user_unfollower
        author = self.user
        client.get(reverse('posts:profile_unfollow',
                   kwargs={'username': 'auth'}))
        follower = Follow.objects.filter(
            user=user,
            author=author
        ).exists()
        self.assertFalse(follower, 'Отписка не работает')

    def test_new_posts_follower(self):
        """Новые посты появляются на странице на кого подписан"""
        client = self.authorized_user_follower_client
        client.get(reverse('posts:profile_follow',
                   kwargs={'username': 'auth'}))
        response_old = client.get(reverse('posts:follow_index'))
        self.assertEqual(len(response_old.context.get('page_obj').object_list),
                         1, 'Неверное кол-во постов')
        Post.objects.create(
            author=self.user,
            text='Тестовый пост2',
            group=self.group
        )
        cache.clear()
        response_new = client.get(reverse('posts:follow_index'))
        self.assertEqual(len(response_new.context.get('page_obj').object_list),
                         2, 'Нету нового поста')

    def test_new_posts_unfollower(self):
        """Посты исчезают если отписался"""
        client = self.authorized_user_unfollower_client
        response_old = client.get(reverse('posts:follow_index'))
        self.assertEqual(len(response_old.context.get('page_obj').object_list),
                         0, 'Неверное кол-во старых постов')
        Post.objects.create(
            author=self.user,
            text='Тестовый пост1',
            group=self.group
        )
        cache.clear()
        response_new = client.get(reverse('posts:follow_index'))
        self.assertEqual(len(response_new.context.get('page_obj').object_list),
                         0, 'Новый пост не должен появляться')
