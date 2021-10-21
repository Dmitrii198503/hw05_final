from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from http import HTTPStatus


User = get_user_model()


class URLTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')

    def setUp(self):
        self.guest_client = Client()

    def test_custom_404(self):
        """page mot found URL matches custom template"""
        address = '/anypage/'
        template = 'core/404.html'
        status = HTTPStatus.NOT_FOUND.value
        response = self.guest_client.get(address, follow=True)
        self.assertTemplateUsed(response, template)
        self.assertEqual(response.status_code, status)
