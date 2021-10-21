from django.test import TestCase, Client, override_settings
from django.contrib.auth import get_user_model
from ..models import Post, Comment
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
import shutil
import tempfile


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateEditTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.image = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x00\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='image.gif',
            content=cls.image,
            content_type='image/gif'
        )
        cls.post_0 = Post.objects.create(
            text='Any',
            author=cls.user
        )
        cls.comment = Comment.objects.create(
            post=cls.post_0,
            author=cls.user,
            text='Test text'
        )

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post_id = self.post_0.pk

    def test_create_post(self):
        post_count = Post.objects.count()
        form_data = {
            'text': 'Test text',
            'image': self.uploaded
        }

        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )

        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.user}))

        self.assertEqual(Post.objects.count(), post_count + 1)

        self.assertTrue(Post.objects.filter(
            text='Test text', image='posts/image.gif').exists()
        )

    def test_edit_post(self):
        primary_post_id = self.post_id
        post_count = Post.objects.count()
        form_data = {
            'text': 'Text to test'
        }

        response = self.authorized_client.post(
            reverse(
                'posts:post_edit', kwargs={'post_id': self.post_id}),
            data=form_data,
            follow=True
        )

        self.assertRedirects(
            response,
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post_id})
        )

        self.assertEqual(Post.objects.count(), post_count)

        self.assertFalse(primary_post_id != self.post_id)

    def test_comment_create_authorized(self):
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Super text'
        }
        response = self.authorized_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': self.post_id}
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post_id})
        )
        self.assertEqual(Comment.objects.count(), comment_count + 1)

    def test_comment_create_guest(self):
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Super text'
        }
        response = self.guest_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': self.post_id}
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            f'/auth/login/?next=/posts/{self.post_id}/comment'
        )
        self.assertTrue(Comment.objects.count() != comment_count + 1)
