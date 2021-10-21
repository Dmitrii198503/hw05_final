from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from http import HTTPStatus


User = get_user_model()


class URLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='TestUser',
                                             password='1234')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template_guest_user(self):
        """URL matches appropriate template for guest user"""
        templates_url_names = {
            '/auth/signup/': 'users/signup.html',
            '/auth/logout/': 'users/logged_out.html',
            '/auth/login/': 'users/login.html',
            '/auth/password_change/': 'users/login.html',
            '/auth/password_change/done/': 'users/login.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/reset/done/': 'users/password_reset_complete.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address, follow=True)
                self.assertTemplateUsed(response, template)

    def test_urls_uses_correct_template_authorized_user(self):
        """URL matches appropriate template for authorized user"""
        templates_url_names = {
            '/auth/signup/': 'users/signup.html',
            '/auth/logout/': 'users/logged_out.html',
            '/auth/login/': 'users/login.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/reset/done/': 'users/password_reset_complete.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address, follow=True)
                self.assertTemplateUsed(response, template)

    def test_HTTP_status_guest(self):
        """URL matches appropriate value for guest user"""
        URL_values = {
            '/auth/signup/': HTTPStatus.OK.value,
            '/auth/logout/': HTTPStatus.OK.value,
            '/auth/login/': HTTPStatus.OK.value,
            '/auth/password_change/': HTTPStatus.FOUND.value,
            '/auth/password_change/done/': HTTPStatus.FOUND.value,
            '/auth/password_reset/': HTTPStatus.OK.value,
            '/auth/password_reset/done/': HTTPStatus.OK.value,
            '/auth/reset/done/': HTTPStatus.OK.value,
        }
        for address, value in URL_values.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, value)

    def test_HTTP_status_authorized(self):
        """URL matches appropriate value for authorized user"""
        URL_values = {
            '/auth/signup/': HTTPStatus.OK.value,
            '/auth/logout/': HTTPStatus.OK.value,
            '/auth/login/': HTTPStatus.OK.value,
            '/auth/password_change/': HTTPStatus.FOUND.value,
            '/auth/password_change/done/': HTTPStatus.FOUND.value,
            '/auth/password_reset/': HTTPStatus.OK.value,
            '/auth/password_reset/done/': HTTPStatus.OK.value,
            '/auth/reset/done/': HTTPStatus.OK.value,
        }
        for address, value in URL_values.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, value)
