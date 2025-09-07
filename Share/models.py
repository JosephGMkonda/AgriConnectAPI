from django.db import models
from django.conf import settings
from posts.models import Post



class Share(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shares')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='shares')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')
        indexes = [
            models.Index(fields=['post'], name='share_post_idx'),
            models.Index(fields=['user'], name='share_user_idx'),
            models.Index(fields=['created_at'], name='share_created_at_idx'),
        ]
        ordering = ['-created_at']
        verbose_name = "Share"
        verbose_name_plural = "Shares"

    def __str__(self):
        return f"Share by {self.user.username} on {self.post.title}"