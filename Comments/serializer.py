from rest_framework import serializers
from .models import Comment
from django.contrib.auth import get_user_model

User = get_user_model()

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)
    class Meta:
        model = Comment
        fields = ['id','author','post','content','created_at','updated_at']
        read_only_fields=['id','author','created_at']
