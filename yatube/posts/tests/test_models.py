from django.contrib.auth import get_user_model
from django.test import TestCase
from ..models import Post, Group


User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая группа' * 100,
        )

    def test_models_have_correct_object_names(self):
        """__str__ models check"""
        post_name = self.post.text[:15]
        group_name = self.group.title
        self.assertEqual(post_name, str(self.post))
        self.assertEqual(group_name, str(self.group))

    def test_help_text(self):
        """help text matches with expected"""
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Выберите группу',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(self.post._meta.get_field(field).help_text,
                                 expected_value)

    def test_verbose_name(self):
        """verbose name matches with expected"""
        field_verbose_name_texts = {
            'text': 'Текст поста',
            'pub_date': 'Дата создания',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_value in field_verbose_name_texts.items():
            with self.subTest(field=field):
                self.assertEqual(self.post._meta.get_field(field).verbose_name,
                                 expected_value)
