from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from posts.models import Post

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        indexes = [
            models.Index(fields=['post'], name='comment_post_idx'),
            models.Index(fields=['author'], name='comment_author_idx'),
            models.Index(fields=['created_at'], name='comment_created_at_idx'),
        ]
        ordering = ['-created_at']
        verbose_name = _("Comment")
        verbose_name_plural = _("Comments")

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"

