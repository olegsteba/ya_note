
import pytest

from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'name',
    ('notes:home', 'users:login', 'users:logout', 'users:signup'),
)
def test_home_availability_for_anonymous_user(client, name):
    """Страницы доступны анонимному пользователю:
    - главная страница;
    - страница авторизации;
    - страница выхода;
    - страница регистрации.
    """
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name',
    ('notes:list', 'notes:add', 'notes:success'),
)
def test_pages_availability_for_auth_user(not_author_client, name):
    """
    Доступность страниц авторизированному пользователю:
    - список заметок notes/;
    - успешное добаление заметки done/;
    - добавление заметки add/.
    """
    url = reverse(name)
    response = not_author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
    ),
)
@pytest.mark.parametrize(
    'name',
    ('notes:detail', 'notes:edit', 'notes:delete'),
)
def test_pages_availability_for_different_users(
    parametrized_client, name, slug_for_args, expected_status
):
    """Доступность страниц для автора заметки статус 200,
    для клиента статус 404:
    - детальный просмотр своей заметки;
    - редактирование своей заметки;
    - удаление своей заметки.
    """
    url = reverse(name, args=slug_for_args)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name, args',
    (
        ('notes:detail', pytest.lazy_fixture('slug_for_args')),
        ('notes:edit', pytest.lazy_fixture('slug_for_args')),
        ('notes:delete', pytest.lazy_fixture('slug_for_args')),
        ('notes:add', None),
        ('notes:success', None),
        ('notes:list', None),
    ),
)
def test_redirects(client, name, args):
    """Перенаправление со страниц:
    - отдельной записи;
    - редактирование запси;
    - удаление записи;
    - добавление записи;
    - успешного добавления записи;
    - со списком записей.
    """
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
