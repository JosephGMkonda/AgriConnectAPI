from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.conf import settings



class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['slug'], name='tag_slug_idx'),
            models.Index(fields=['name'], name='tag_name_idx'),
        ]

    def __str__(self):
        return self.name


class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=200)
    content = models.TextField()
    image_url = models.URLField(max_length=500, blank=True, null=True)
    video_url = models.URLField(max_length=500, blank=True, null=True)
    tags = models.ManyToManyField(Tag, related_name='posts', blank=True)
    view_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        indexes = [
            models.Index(fields=['author'], name='post_author_idx'),
            models.Index(fields=['created_at'], name='post_created_at_idx'),
            models.Index(fields=['-view_count'], name='post_view_count_idx'),
        ]

        ordering = ['-created_at']
        verbose_name = _("Post")
        verbose_name_plural = _("Posts")
    def __str__(self):
        return self.title
