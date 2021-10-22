from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from ..models import Group, Post
from http import HTTPStatus
from django.urls import reverse


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
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_posts',
                    kwargs={'slug': self.slug}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': self.user}): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post_id}
            ): 'posts/post_detail.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post_id}): 'users/login.html',
            reverse('posts:post_create'): 'users/login.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address, follow=True)
                self.assertTemplateUsed(response, template)

    def test_urls_uses_correct_template_authorized_user(self):
        """URL matches appropriate template for authorized user"""
        templates_url_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_posts',
                    kwargs={'slug': self.slug}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': self.user}): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post_id}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post_id}
            ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_HTTP_status_guest(self):
        """URL matches appropriate value for guest user"""
        URL_values = {
            reverse('posts:index'): HTTPStatus.OK.value,
            reverse('posts:group_posts',
                    kwargs={'slug': self.slug}): HTTPStatus.OK.value,
            reverse('posts:profile',
                    kwargs={'username': self.user}): HTTPStatus.OK.value,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post_id}
            ): HTTPStatus.OK.value,
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post_id}
            ): HTTPStatus.FOUND.value,
            reverse('posts:post_create'): HTTPStatus.FOUND.value,
            '/unexisting_page/': HTTPStatus.NOT_FOUND.value,
        }
        for address, value in URL_values.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, value)

    def test_HTTP_status_authorized(self):
        """URL matches appropriate value for authorized user"""
        URL_values = {
            reverse('posts:index'): HTTPStatus.OK.value,
            reverse('posts:group_posts',
                    kwargs={'slug': self.slug}): HTTPStatus.OK.value,
            reverse('posts:profile',
                    kwargs={'username': self.user}): HTTPStatus.OK.value,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post_id}
            ): HTTPStatus.OK.value,
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post_id}
            ): HTTPStatus.OK.value,
            reverse('posts:post_create'): HTTPStatus.OK.value,
            '/unexisting_page/': HTTPStatus.NOT_FOUND.value,
        }
        for address, value in URL_values.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, value)
