from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note


User = get_user_model()


class TestNotesListPages(TestCase):
    """Тестирование страницы заметок авторизированного пользователя."""

    NOTES_LIST_URL = reverse("notes:list")
    NOTES_ADD_URL = reverse("notes:add")

    @classmethod
    def setUpTestData(cls):
        cls.user_first = User.objects.create(username="user_first_1")
        cls.user_second = User.objects.create(username="user_second_2")
        all_notes = [
            Note(
                title=f"Заголовок {index}",
                text="Текст сообщения",
                slug=f"zagolovok_{index}",
                author=cls.user_first,
            )
            for index in range(4)
        ]
        all_notes += [
            Note(
                title=f"Заголовок {index}",
                text="Текст сообщения",
                slug=f"zagolovok_{index}",
                author=cls.user_second,
            )
            for index in range(4, 10)
        ]
        Note.objects.bulk_create(all_notes)

    def test_showing_notes_to_author(self):
        """Показ собственных заметок для авторизированного пользователя."""
        self.client.force_login(self.user_first)
        response = self.client.get(self.NOTES_LIST_URL)
        notes_list = response.context["note_list"]
        notes_count = notes_list.count()
        objects_count = Note.objects.filter(author=self.user_first).count()
        self.assertEqual(notes_count, objects_count)

    def test_notes_to_author_order(self):
        """Сортировка заметок пользователя по возрастанию от старых к новым"""
        self.client.force_login(self.user_second)
        response = self.client.get(self.NOTES_LIST_URL)
        notes_list = response.context["note_list"]
        all_timestamp = [note.id for note in notes_list]
        sorted_timestamp = sorted(all_timestamp)
        self.assertEqual(all_timestamp, sorted_timestamp)

    def test_autorized_client_has_note_form(self):
        """Наличие формы добавления заметки у авторизированного пользователя"""
        self.client.force_login(self.user_first)
        response = self.client.get(self.NOTES_ADD_URL)
        self.assertIn("form", response.context)
        self.assertIsInstance(response.context["form"], NoteForm)
