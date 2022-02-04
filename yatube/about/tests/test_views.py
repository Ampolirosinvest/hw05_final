# Необязательное задание
from django.test import TestCase, Client
from django.urls import reverse


class StaticURLTests(TestCase):
    def setUp(self):
        # Устанавливаем данные для тестирования
        # Создаём экземпляр клиента. Он неавторизован.
        self.guest_client = Client()

    # Проверка шаблонов
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон about."""
        # Собираем в словарь пары reverse(name): имя_шаблона"
        templates_pages_names = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
        }
        # Проверяем, что при обращении к name вызывается соответ. HTML-шаблон
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
