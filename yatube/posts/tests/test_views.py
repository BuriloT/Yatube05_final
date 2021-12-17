import shutil
import tempfile
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile

from posts.models import Post, Group, Follow


User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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
        cls.user = User.objects.create(username='Name')
        cls.group = Group.objects.create(
            title='Test',
            description='Test_Group',
            slug='text-slug'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст',
            group=cls.group,
            image=uploaded
        )
        cls.group_2 = Group.objects.create(
            title='Test-2',
            description='Test_Group',
            slug='test-slug'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.__class__.user)
        self.post_id = PostPagesTest.post.id

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': (
                reverse('posts:group_list', kwargs={'slug': 'text-slug'})),
            'posts/profile.html': (
                reverse('posts:profile',
                        kwargs={'username': PostPagesTest.user})),
            'posts/post_detail.html': (
                reverse('posts:post_detail',
                        kwargs={'post_id': self.post_id})),
            'posts/create_post.html': reverse('posts:post_create'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_edit_use_correct_template(self):
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post_id}))
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_home_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        post = response.context['page_obj'][0]
        text = post.text
        author = post.author
        group = post.group
        image = post.image
        self.assertEqual(text, self.post.text)
        self.assertEqual(author, self.post.author)
        self.assertEqual(group, self.post.group)
        self.assertEqual(image, self.post.image)

    def test_group_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'text-slug'})
        )
        post = response.context['page_obj'][0]
        group = post.group
        author = post.author
        image = post.image
        self.assertEqual(post, self.post)
        self.assertEqual(group, self.group)
        self.assertEqual(author, self.post.author)
        self.assertEqual(image, self.post.image)

    def test_profile_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'Name'})
        )
        post = response.context['page_obj'][0]
        text = post.text
        author = post.author
        group = post.group
        image = post.image
        self.assertEqual(text, self.post.text)
        self.assertEqual(author, self.post.author)
        self.assertEqual(group, self.group)
        self.assertEqual(image, self.post.image)

    def test_post_detail_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        post = response.context.get('posts')
        text = post.text
        author = post.author
        group = post.group
        image = post.image
        self.assertEqual(text, self.post.text)
        self.assertEqual(author, self.post.author)
        self.assertEqual(group, self.group)
        self.assertEqual(image, self.post.image)

    def test_create_post_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_in_group(self):
        posts_group = Post.objects.filter(
            group=self.group
        ).count()
        self.assertEqual(posts_group, Post.objects.count())
        Post.objects.create(
            text='Text',
            author=self.user,
            group=self.group
        )
        self.assertEqual(Post.objects.count(), posts_group + 1)
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 2)
        response = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}))
        self.assertEqual(len(response.context['page_obj']), 2)
        response = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': self.group_2.slug}))
        self.assertEqual(len(response.context['page_obj']), 0)
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user}))
        self.assertEqual(len(response.context['page_obj']), 2)

    def test_cache_home_page(self):
        response = self.authorized_client.get(reverse('posts:index'))
        Post.objects.all().delete()
        response_2 = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response.content, response_2.content)
        cache.clear()
        response_3 = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(response.content, response_3.content)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='UserName')
        cls.group = Group.objects.create(
            title='Test',
            description='Test_Group',
            slug='text-slug'
        )
        for i in range(13):
            Post.objects.create(
                author=cls.user,
                text='Текст {i}',
                group=cls.group,
            )

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.__class__.user)

    def test_paginator(self):
        pages = {
            reverse('posts:index'): 10,
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}): 10,
            reverse('posts:profile',
                    kwargs={'username': self.user}): 10,
            reverse('posts:index') + '?page=2': 3,
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}) + '?page=2': 3,
            reverse('posts:profile',
                    kwargs={'username': self.user}) + '?page=2': 3
        }
        for reverse_name, posts in pages.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']), posts)


class FollowViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='Author')
        cls.user = User.objects.create(username='User')

    def setUp(self):
        self.user1 = Client()
        self.user2 = Client()
        self.user1.force_login(self.user)
        self.user2.force_login(self.author)

    def test_follow(self):
        count = Follow.objects.count()
        self.user1.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.author}
            )
        )
        Follow.objects.count()
        self.assertEqual(count + 1, Follow.objects.count())
        self.user1.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.author}
            )
        )
        self.assertEqual(count, Follow.objects.count())

    def test_follow_new_post(self):
        Follow.objects.create(user=self.user, author=self.author)
        post = Post.objects.create(author=self.author, text='Текст')
        response = self.user1.get(reverse(
            'posts:follow_index'
        ))
        self.assertIn(post, response.context['page_obj'])

    def test_nofollow_new_post(self):
        post = Post.objects.create(author=self.author, text='Текст')
        response = self.user1.get(reverse(
            'posts:follow_index'
        ))
        self.assertNotIn(post, response.context['page_obj'])
