from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestNoteCreate(TestCase):
    """Тестирование создание заметок"""

    NOTE_DATA = {
        'title': 'Заголовок 1',
        'text': 'Текст заметки',
        'slug': 'zametka_1',
    }

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('notes:add')
        cls.success_url = reverse('notes:success')
        cls.user = User.objects.create(username='ole')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = cls.NOTE_DATA

    def test_anonymous_cant_create_note(self):
        """Анонимный пользователь не может создавать записи."""
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_can_create_note(self):
        """Авторизованный пользователь может создавать записи."""
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.NOTE_DATA['title'])
        self.assertEqual(note.text, self.NOTE_DATA['text'])
        self.assertEqual(note.slug, self.NOTE_DATA['slug'])
        self.assertEqual(note.author, self.user)


class TestNoteEditDelete(TestCase):
    """Тестирование редактирование и удаление записей."""

    NOTE_DATA = {
        'title': 'Заголовок 1',
        'text': 'Текст заметки',
        'slug': 'zametka_1',
    }
    NOTE_NEW_DATA = {
        'title': 'Заголовок новый',
        'text': 'Текст заметки новый',
        'slug': 'zametka_new',
    }

    @classmethod
    def setUpTestData(cls):
        cls.success_url = reverse('notes:success')
        cls.author = User.objects.create(username='author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='reader')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title=cls.NOTE_DATA['title'],
            text=cls.NOTE_DATA['text'],
            slug=cls.NOTE_DATA['slug'],
            author=cls.author,
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = cls.NOTE_NEW_DATA

    def test_author_can_delete_note(self):
        """Автор может удалить свою запись."""
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.success_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_cantdelete_note_of_another_user(self):
        """Пользователь не может удалять чужие записи."""
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_note(self):
        """Автор может редактировать свою запись."""
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NOTE_NEW_DATA['title'])
        self.assertEqual(self.note.text, self.NOTE_NEW_DATA['text'])
        self.assertEqual(self.note.slug, self.NOTE_NEW_DATA['slug'])

    def test_user_cantdelete_note_of_another_user(self):
        """Пользователь не может редактировать чужие записи."""
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NOTE_DATA['title'])
        self.assertEqual(self.note.text, self.NOTE_DATA['text'])
        self.assertEqual(self.note.slug, self.NOTE_DATA['slug'])

    def test_db_contains_onenote(self):
        """В БД содержится одна запись."""
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
