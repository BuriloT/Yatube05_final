import shutil
import tempfile
from http import HTTPStatus
from django.test import Client, TestCase, override_settings
from django.conf import settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from posts.models import Group, Post, Comment
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Name')
        cls.Group = Group.objects.create(
            title='Test',
            description='Test_Group',
            slug='text-slug'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст',
            group=cls.Group,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest = Client()
        self.authorized_author = Client()
        self.authorized_author.force_login(__class__.user)

    def test_create_post(self):
        post_count = Post.objects.count()
        small_gif = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
                     b'\x01\x00\x80\x00\x00\x00\x00\x00'
                     b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                     b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                     b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                     b'\x0A\x00\x3B')
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Текст',
            'group': '1',
            'author': self.user,
            'image': uploaded
        }
        response = self.authorized_author.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response,
                             reverse('posts:profile',
                                     kwargs={'username': 'Name'}))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                group='1',
                text='Текст',
                author=self.user,
                image='posts/small.gif'
            ).exists()
        )

    def test_post_edit(self):
        post_count = Post.objects.count()
        small_gif = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
                     b'\x01\x00\x80\x00\x00\x00\x00\x00'
                     b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                     b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                     b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                     b'\x0A\x00\x3B')
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Текст',
            'image': uploaded
        }
        response = self.authorized_author.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response,
                             reverse('posts:post_detail',
                                     kwargs={'post_id': self.post.id}))
        self.assertEqual(Post.objects.count(), post_count)
        self.assertTrue(
            Post.objects.filter(
                text='Текст',
                image='posts/small.gif'
            ).exists
        )


class CommentFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Maniken')
        cls.post = Post.objects.create(
            text='Текст',
            author=cls.user
        )

    def setUp(self):
        self.guest = Client()
        self.authorized_author = Client()
        self.authorized_author.force_login(__class__.user)

    def test_create_comment(self):
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Нужный текст'
        }
        response = self.authorized_author.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response,
                             reverse('posts:post_detail',
                                     kwargs={'post_id': self.post.id}))
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertTrue(
            Comment.objects.filter(text='Нужный текст').exists()
        )

    def test_guest_create_comment(self):
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Нужный текст'
        }
        response = self.guest.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, '/auth/login/?next=/posts/1/comment/')
        self.assertEqual(Comment.objects.count(), comment_count)
        self.assertFalse(
            Comment.objects.filter(text='Нужный текст').exists()
        )
