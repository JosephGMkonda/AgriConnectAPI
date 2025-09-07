from django.db import models
from django.conf import settings
from posts.models import Post

class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')
        indexes = [
            models.Index(fields=['post'], name='like_post_idx'),
            models.Index(fields=['user'], name='like_user_idx'),
            models.Index(fields=['created_at'], name='like_created_at_idx'),
        ]
        ordering = ['-created_at']
        

    def __str__(self):
        return f"Like by {self.user.username} on {self.post.title}"
