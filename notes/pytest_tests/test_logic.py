import pytest

from http import HTTPStatus
from pytils.translit import slugify
from pytest_django.asserts import assertRedirects, assertFormError

from django.urls import reverse

from notes.models import Note
from notes.forms import WARNING


pytestmark = [pytest.mark.django_db]

URL_NOTE_ADD = reverse('notes:add')
URL_NOTE_SUCCESS = reverse('notes:success')
URL_LOGIN = reverse('users:login')



def test_user_can_create_note(author_client, author, form_data):
    """Создание заметки авторизированным пользователем."""
    response = author_client.post(URL_NOTE_ADD, data=form_data)
    assertRedirects(response, URL_NOTE_SUCCESS)
    assert Note.objects.count() == 1
    new_note = Note.objects.get()
    assert new_note.title == form_data['title']
    assert new_note.text == form_data['text']
    assert new_note.slug == form_data['slug']
    assert new_note.author == author


def test_anonymous_user_cant_create_note(client, form_data):
    """Создание заметки анонимным пользователем."""
    response = client.post(URL_NOTE_ADD, data=form_data)
    expected_url = f'{URL_LOGIN}?next={URL_NOTE_ADD}'
    assertRedirects(response, expected_url)
    assert Note.objects.count() == 0


def test_not_unique_slug(author_client, note, form_data):
    """Уникальность slug."""
    form_data['slug'] = note.slug
    response = author_client.post(URL_NOTE_ADD, data=form_data)
    assertFormError(response, 'form', 'slug', errors=(note.slug + WARNING))
    assert Note.objects.count() == 1


def test_empty_slug(author_client, form_data):
    """Автоматическое создание slug при пустом значении."""
    form_data.pop('slug')
    response = author_client.post(URL_NOTE_ADD, data=form_data)
    assertRedirects(response, URL_NOTE_SUCCESS)
    assert Note.objects.count() == 1
    new_note = Note.objects.get()
    expected_slug = slugify(form_data['title'])
    assert new_note.slug == expected_slug


def test_author_can_edit_note(author_client, form_data, note):
    """Редактирование записи автором."""
    url = reverse('notes:edit', args=(note.slug, ))
    response = author_client.post(url, form_data)
    assertRedirects(response, URL_NOTE_SUCCESS)
    note.refresh_from_db()
    assert note.title == form_data['title']
    assert note.text == form_data['text']
    assert note.slug == form_data['slug']


def test_other_cant_edit_note(not_author_client, form_data, note):
    """Редактирование записи не автором невозможно."""
    url = reverse('notes:edit', args=(note.slug, ))
    response = not_author_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    note_from_db = Note.objects.get(id=note.id)
    assert note.title == note_from_db.title
    assert note.text == note_from_db.text
    assert note.slug == note_from_db.slug


def test_author_can_delete_note(author_client, slug_for_args):
    """Удаление записи автором."""
    url = reverse('notes:delete', args=slug_for_args)
    response = author_client.post(url)
    assertRedirects(response, URL_NOTE_SUCCESS)
    assert Note.objects.count() == 0


def test_other_user_cant_delete_note(not_author_client, slug_for_args):
    """Удаление записи не автором не возможно."""
    url = reverse('notes:delete', args=slug_for_args)
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Note.objects.count() == 1
