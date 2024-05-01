from http import HTTPStatus

from django.urls import reverse

from notes.tests.core import CoreTestCase, URLS


class TestRoutes(CoreTestCase):
    """Тестирование доступности конкретных маршрутов."""

    def test_page_availability(self):
        """Доступность страниц для ананимного пользователя."""
        urls = (
            (URLS['home'], None),
            (URLS['login'], None),
            (URLS['logout'], None),
            (URLS['signup'], None),
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
        self.note.refresh_from_db()
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.user, HTTPStatus.NOT_FOUND),
        )
        urls = (
            (URLS['edit'], (self.note.slug,)),
            (URLS['detail'], (self.note.slug,)),
            (URLS['delete'], (self.note.slug,)),
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
        self.note.refresh_from_db()
        login_url = reverse(URLS['login'])
        urls = (
            (URLS['add'], None),
            (URLS['edit'], (self.note.slug,)),
            (URLS['detail'], (self.note.slug,)),
            (URLS['delete'], (self.note.slug,)),
            (URLS['list'], None),
            (URLS['success'], None),
        )

        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
