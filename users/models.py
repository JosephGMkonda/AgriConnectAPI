from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    supabase_uid = models.CharField(max_length=255, unique=True, null=True, blank=True)
    

    def __str__(self):
        return self.username
