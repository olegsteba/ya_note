from http import HTTPStatus

from pytils.translit import slugify

from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note
from notes.tests.core import CoreTestCase, NOTE_DATA, NOTE_NEW_DATA, URLS


class TestNoteCreate(CoreTestCase):
    """Тестирование создание заметок"""

    def test_anonymous_cant_create_note(self):
        """Анонимный пользователь не может создавать записи."""
        notes_count = Note.objects.count()
        self.client.post(reverse(URLS['add']), data=self.form_new_data)
        new_notes_count = Note.objects.count()
        self.assertEqual(notes_count, new_notes_count)

    def test_user_can_create_note(self):
        """Авторизованный пользователь может создавать записи."""
        notes_count = Note.objects.count()
        response = self.author_client.post(
            reverse(URLS['add']),
            data=self.form_new_data
        )
        self.assertRedirects(response, reverse(URLS['success']))
        new_notes_count = Note.objects.count()
        self.assertEqual(notes_count + 1, new_notes_count)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, NOTE_DATA['title'])
        self.assertEqual(self.note.text, NOTE_DATA['text'])
        self.assertEqual(self.note.slug, NOTE_DATA['slug'])
        self.assertEqual(self.note.author, self.author)

    def test_not_unique_slug(self):
        """Уникальность slug."""
        notes_count = Note.objects.count()
        response = self.author_client.post(
            reverse(URLS['add']),
            data=self.form_data
        )
        self.assertFormError(
            response,
            'form',
            field='slug',
            errors=(self.form_data['slug'] + WARNING),
        )
        new_notes_count = Note.objects.count()
        self.assertEqual(notes_count, new_notes_count)

    def test_empty_slug(self):
        """Автоматическое создание slug при пустом значении."""
        self.form_new_data.pop('slug')
        notes_count = Note.objects.count()
        response = self.author_client.post(
            reverse(URLS['add']),
            data=self.form_new_data
        )
        new_notes_count = Note.objects.count()
        self.assertRedirects(response, reverse(URLS['success']))
        self.assertEqual(notes_count + 1, new_notes_count)
        self.note.refresh_from_db()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(self.note.slug, expected_slug)


class TestNoteEditDelete(CoreTestCase):
    """Тестирование редактирование и удаление записей."""

    def test_author_can_delete_note(self):
        """Автор может удалить свою запись."""
        notes_count = Note.objects.count()
        response = self.author_client.delete(
            reverse(URLS['delete'], args=(self.note.slug, ))
        )
        self.assertRedirects(response, reverse(URLS['success']))
        new_notes_count = Note.objects.count()
        self.assertEqual(notes_count - 1, new_notes_count)

    def test_user_cant_delete_note_of_another_user(self):
        """Пользователь не может удалять чужие записи."""
        notes_count = Note.objects.count()
        response = self.user_client.delete(
            reverse(URLS['delete'], args=(self.note.slug, ))
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        new_notes_count = Note.objects.count()
        self.assertEqual(notes_count, new_notes_count)

    def test_author_can_edit_note(self):
        """Автор может редактировать свою запись."""
        response = self.author_client.post(
            reverse(URLS['edit'], args=(self.note.slug, )),
            data=self.form_new_data
        )
        self.assertRedirects(response, reverse(URLS['success']))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, NOTE_NEW_DATA['title'])
        self.assertEqual(self.note.text, NOTE_NEW_DATA['text'])
        self.assertEqual(self.note.slug, NOTE_NEW_DATA['slug'])

    def test_user_cantdelete_note_of_another_user(self):
        """Пользователь не может редактировать чужие записи."""
        response = self.user_client.post(
            reverse(URLS['edit'], args=(self.note.slug, )),
            data=self.form_new_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, NOTE_DATA['title'])
        self.assertEqual(self.note.text, NOTE_DATA['text'])
        self.assertEqual(self.note.slug, NOTE_DATA['slug'])
