from django.db import models
from django.conf import settings


class Follow(models.Model):
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')
        indexes = [
            models.Index(fields=['follower'], name='follow_follower_idx'),
            models.Index(fields=['following'], name='follow_following_idx'),
            models.Index(fields=['created_at'], name='follow_created_at_idx'),
        ]
        ordering = ['-created_at']
        verbose_name = "Follow"
        verbose_name_plural = "Follows"

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"