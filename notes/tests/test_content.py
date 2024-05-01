from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm
from notes.tests.core import CoreTestCase, URLS


class TestNotesListPages(CoreTestCase):
    """Тестирование страницы заметок авторизированного пользователя."""

    @classmethod
    def setUpTestData(cls):
        super(TestNotesListPages, cls).setUpTestData()
        cls.notes = [
            Note(
                title=f"Заголовок {index}",
                text="Текст сообщения",
                slug=f"zagolovok_{index}",
                author=cls.author,
            )
            for index in range(4)
        ]
        cls.notes += [
            Note(
                title=f"Заголовок {index}",
                text="Текст сообщения",
                slug=f"zagolovok_{index}",
                author=cls.user,
            )
            for index in range(4, 10)
        ]
        Note.objects.bulk_create(cls.notes)

    def test_showing_notes_to_author(self):
        """Показ собственных заметок для авторизированного пользователя."""
        response = self.author_client.get(reverse(URLS['list']))
        notes_list = response.context["note_list"]
        notes_count = notes_list.count()
        objects_count = Note.objects.filter(author=self.author).count()
        self.assertEqual(notes_count, objects_count)

    def test_notes_to_author_order(self):
        """Сортировка заметок пользователя по возрастанию от старых к новым"""
        response = self.author_client.get(reverse(URLS['list']))
        notes_list = response.context["note_list"]
        all_notes = [note.id for note in notes_list]
        sorted_notes = sorted(all_notes)
        self.assertEqual(all_notes, sorted_notes)

    def test_autorized_client_has_note_form(self):
        """Наличие формы добавления заметки
        у авторизированного пользователя.
        """
        response = self.author_client.get(reverse(URLS['add']))
        self.assertIn("form", response.context)
        self.assertIsInstance(response.context["form"], NoteForm)
