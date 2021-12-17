from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus

from posts.models import Group, Post


User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug='test-slug'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая группа'
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author = Client()
        self.author.force_login(self.__class__.user)
        self.guest_urls = ['/', f'/group/{self.group.slug}/',
                           f'/posts/{self.post.id}/',
                           f'/profile/{self.user}/']
        self.authorized_urls = ['/create/', f'/posts/{self.post.id}/edit/']

    def test_guest_urls(self):
        for urls in self.guest_urls:
            with self.subTest(urls=urls):
                response = self.guest_client.get(urls)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_authorized_urls(self):
        self.authorized_urls += self.guest_urls
        for urls in self.authorized_urls:
            with self.subTest(urls=urls):
                response = self.author.get(urls)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_page_url(self):
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_post_create_redirect_anonymous_on_admin_login(self):
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_post_edit_redirect_anonymous_on_admin_login(self):
        response = self.guest_client.get('/posts/1/edit/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/posts/1/edit/')

    def test_post_edit_redirect_authorized_client_on_admin_login(self):
        response = self.authorized_client.get('/posts/1/edit/', follow=True)
        self.assertRedirects(response, '/posts/1/')

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': '/group/test-slug/',
            'posts/profile.html': '/profile/HasNoName/',
            'posts/post_detail.html': '/posts/1/',
            'posts/create_post.html': '/create/'
        }
        for template, adress in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_post_edit_use_correct_template(self):
        response = self.author.get('/posts/1/edit/')
        self.assertTemplateUsed(response, 'posts/create_post.html')
