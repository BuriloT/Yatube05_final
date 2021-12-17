from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus

User = get_user_model()


class UsersURLTests(TestCase):

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_signup_url(self):
        response = self.guest_client.get('/auth/signup/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_login_url(self):
        response = self.guest_client.get('/auth/login/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_logout_url(self):
        response = self.guest_client.get('/auth/logout/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_change_url(self):
        response = self.authorized_client.get('/auth/password_change/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_change_done_url(self):
        response = self.authorized_client.get('/auth/password_change/done/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_reset_url(self):
        response = self.guest_client.get('/auth/password_reset/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_reset_done_url(self):
        response = self.guest_client.get('/auth/password_reset/done/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
