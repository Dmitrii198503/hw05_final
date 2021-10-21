from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from ..models import Group, Post
from http import HTTPStatus


User = get_user_model()


class URLTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='Group',
            slug='test-slug',
            description='Any',
        )
        cls.post = Post.objects.create(
            text='Any',
            author=cls.user,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post_id = self.post.pk
        self.slug = self.group.slug

    def test_urls_uses_correct_template_guest_user(self):
        """URL matches appropriate template for guest user"""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.slug}/': 'posts/group_list.html',
            '/profile/TestUser/': 'posts/profile.html',
            f'/posts/{self.post_id}/': 'posts/post_detail.html',
            f'/posts/{self.post_id}/edit/': 'users/login.html',
            '/create/': 'users/login.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address, follow=True)
                self.assertTemplateUsed(response, template)

    def test_urls_uses_correct_template_authorized_user(self):
        """URL matches appropriate template for authorized user"""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.slug}/': 'posts/group_list.html',
            '/profile/TestUser/': 'posts/profile.html',
            f'/posts/{self.post_id}/': 'posts/post_detail.html',
            f'/posts/{self.post_id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_HTTP_status_guest(self):
        """URL matches appropriate value for guest user"""
        URL_values = {
            '/': HTTPStatus.OK.value,
            f'/group/{self.slug}/': HTTPStatus.OK.value,
            '/profile/TestUser/': HTTPStatus.OK.value,
            f'/posts/{self.post_id}/': HTTPStatus.OK.value,
            f'/posts/{self.post_id}/edit/': HTTPStatus.FOUND.value,
            '/create/': HTTPStatus.FOUND.value,
            '/unexisting_page/': HTTPStatus.NOT_FOUND.value,
        }
        for address, value in URL_values.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, value)

    def test_HTTP_status_authorized(self):
        """URL matches appropriate value for authorized user"""
        URL_values = {
            '/': HTTPStatus.OK.value,
            f'/group/{self.slug}/': HTTPStatus.OK.value,
            '/profile/TestUser/': HTTPStatus.OK.value,
            f'/posts/{self.post_id}/': HTTPStatus.OK.value,
            f'/posts/{self.post_id}/edit/': HTTPStatus.OK.value,
            '/create/': HTTPStatus.OK.value,
            '/unexisting_page/': HTTPStatus.NOT_FOUND.value,
        }
        for address, value in URL_values.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, value)
