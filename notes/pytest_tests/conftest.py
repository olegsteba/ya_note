import pytest

from django.test.client import Client

from notes.models import Note


@pytest.fixture
def author(django_user_model):
    """Фикстура автора заметки."""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    """Фикстура обычного пользователя."""
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    """Активация автора."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    """Активация не автора."""
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def note(author):
    """Объект заметки."""
    note = Note.objects.create(
        title='Заголовок',
        text='Текст заметки',
        slug='note-slug',
        author=author
    )
    return note


@pytest.fixture
def slug_for_args(note):
    """Возвращает кортеж который содержит слаг заметки (url-адрес)."""
    return (note.slug,)


@pytest.fixture
def form_data():
    """Значение формы записи."""
    return {
        'title': 'Новый заголовок',
        'text': 'Новый текст',
        'slug': 'new-slug',
    }
