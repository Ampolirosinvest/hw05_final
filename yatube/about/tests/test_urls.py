from http.client import OK
from django.test import TestCase, Client


class StaticURLTests(TestCase):
    def setUp(self):
        # Устанавливаем данные для тестирования
        # Создаём экземпляр клиента. Он неавторизован.
        self.guest_client = Client()

    def test_about_all(self):
        # Отправляем запрос через client,
        # созданный в setUp()
        response_all = {
            '/about/tech/': OK,
            '/about/author/': OK,
        }
        for name, code in response_all .items():
            with self.subTest(name=name):
                response = self.guest_client.get(name)
                self.assertEqual(response.status_code, code)

    def test_shablon_all(self):
        # Отправляем запрос через client,
        # созданный в setUp()
        response_all = {
            'about/tech.html': '/about/tech/',
            'about/author.html': '/about/author/',
        }
        for template, address in response_all .items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    # На стлучай если неавторизированный пользователь
    # попробует ввести в строке адреса страниц
    # создания и регистрации поста его туда не пустит
    def test_guest_client_dostup(self):
        """Тест на отказ в достпе неавторизированнуму пользователю
        при попытке войти в create или edit"""
        url_names = {
            'posts:post_edit': OK,
            'posts:post_create': OK,
        }
        for address, code_url in url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, code_url)
