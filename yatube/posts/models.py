from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Post(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    group = models.ForeignKey('Group',
                              on_delete=models.SET_NULL,
                              blank=True, null=True,
                              related_name='posts')
    image = models.ImageField(upload_to='posts/',
                              blank=True)

    def __str__(self):
        return self.text[:15]

    class Meta:
        ordering = ['-pub_date']


class Group(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    slug = models.SlugField(max_length=200, unique=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE,
        blank=True, null=True,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    def __str__(self):
        return self.text[:15]

    class Meta:
        ordering = ['-created']


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        ordering = ['-id']
