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

class Media(models.Model):
    MEDIA_TYPES = [
        ('image','Image'),
        ('video','Video')
    ]
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='media_files')
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES)
    file_url = models.URLField(max_length=500)
    thumbnail_url = models.URLField(max_length=500,blank=True,null=True)
    alt_text = models.CharField(max_length=200,blank=True)
    order = models.PositiveIntegerField(default=0)
    file_size = models.PositiveIntegerField(default=0)
    duration = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']
        indexes = [
            models.Index(fields=['post','order'])
        ]
    def __str__(self):
        return f"{self.media_type} for Post #{self.post_id}"
        



class Post(models.Model):
    POST_TYPES = [
        ('question', 'Question'),
        ('article', 'Article'),
        ('advice', 'Advice'),
        ('news', 'News'),
        ('tip', 'Farming Tip')

    ]

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=200)
    content = models.TextField()
    post_type = models.CharField(max_length=20, choices=POST_TYPES, default='article')
    tags = models.ManyToManyField(Tag, related_name='posts', blank=True)
    view_count = models.PositiveIntegerField(default=0)
    like_count = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)
    share_count = models.PositiveIntegerField(default=0)
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
    
    def increment_view_count(self):
        Post.objects.filter(id=self.id).update(view_count=models.F('view_count') + 1)

    def update_comment_count(self):
        self.comment_count = self.comments.filter(is_active=True).count()
        self.save(update_fields=['comment_count'])
    @property
    def has_media(self):
        return self.media_files.exists()
    @property
    def primary_media(self):
        return self.media_files.first()
    
