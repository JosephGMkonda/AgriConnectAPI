from django.db import models
from django.conf import settings
from posts.models import Post


class Saved(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saves')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='saves')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')
        indexes = [
            models.Index(fields=['post'], name='saved_post_idx'),
            models.Index(fields=['user'], name='saved_user_idx'),
            models.Index(fields=['created_at'], name='saved_created_at_idx'),
        ]
        ordering = ['-created_at']
        verbose_name = "Saved"
        verbose_name_plural = "Saves"

    def __str__(self):
        return f"Saved by {self.user.username} on {self.post.title}"