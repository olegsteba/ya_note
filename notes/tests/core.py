from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from notes.models import Note


USER_MODEL = get_user_model()
AUTHOR = 'Автор'
USER = 'Пользователь'
ANON = 'Анонимуc'
NOTE_DATA = {
    'title': 'Заголовок',
    'text': 'Текст заметки',
    'slug': 'zametka',
}
NOTE_NEW_DATA = {
    'title': 'Заголовок новый',
    'text': 'Текст заметки новый',
    'slug': 'zametka_new',
}
URLS = {
    'home': 'notes:home',
    'add': 'notes:add',
    'list': 'notes:list',
    'detail': 'notes:detail',
    'edit': 'notes:edit',
    'delete': 'notes:delete',
    'success': 'notes:success',
    'login': 'users:login',
    'logout': 'users:logout',
    'signup': 'users:signup',
}


class CoreTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = USER_MODEL.objects.create(username=AUTHOR)
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.user = USER_MODEL.objects.create(username=USER)
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)
        cls.form_data = NOTE_DATA
        cls.forn_new_data = NOTE_NEW_DATA
        # cls.note = Note.objects.create(
        #     title=NOTE_DATA['title'],
        #     text=NOTE_DATA['text'],
        #     slug=NOTE_DATA['slug'],
        #     author=cls.author
        # )
