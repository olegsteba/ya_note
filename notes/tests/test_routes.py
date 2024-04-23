from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):
    """Тестирование доступности конкретных маршрутов."""

    @classmethod
    def setUpTestData(cls):
        cls.guest_client = Client()
        cls.author = User.objects.create(username='author')
        cls.reader = User.objects.create(username='reader')
        cls.note = Note.objects.create(
            title='Тестовый заголовок',
            text='Тестовая запись заметки',
            author=cls.author
        )

    def test_page_availability(self):
        """Доступность страниц для ананимного пользователя."""
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_author_note_for_detail_edit_delete(self):
        """
        Проверка на доступность страниц записей для автора.
        Проверяемые страницы:
        - редактирование записи, маршрут 'notes:edit';
        - детальный просмотр записи, маршрут 'notes:detail';
        - удаление записи, маршрут 'notes:delete'.
        """
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        urls = (
            ('notes:edit', (self.note.slug,)),
            ('notes:detail', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        )

        for user, status in users_statuses:
            self.client.force_login(user)
            for name, args in urls:
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=args)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """
        Перенаправление ананимного пользователя на страницу авторизации.
        Проверяемые страницы:
        - добавление записи, маршрут 'notes:add';
        - редактирование записи, маршрут 'notes:edit';
        - детальный просмотр записи, маршрут 'notes:detail';
        - удаление записи, маршрут 'notes:delete';
        - просмотр списка записей, мфршрут 'notes:list';
        - страница удачного входа, маршрут 'notes:success'.
        """
        login_url = reverse('users:login')
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
            ('notes:detail', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
            ('notes:list', None),
            ('notes:success', None),
        )

        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
