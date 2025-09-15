from rest_framework import serializers
from .models import Post,Tag
from django.contrib.auth import get_user_model
from Like.models import Like


User = get_user_model()

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        models = Tag
        fields = ['id', 'name', 'slug', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class PostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    tags_ids = serializers.ListField(
        child=serializers.IntegerField(), 
        write_only=True, 
        required=False,
    )
    is_liked = serializers.SerializerMethodField()
    like_count = serializers.IntegerField(read_only=True)
    comment_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Post
        fields = [
            'id', 'author', 'title', 'content', 'post_type', 'image_url', 
            'video_url', 'tags', 'tags_ids',   # ✅ added
            'view_count', 'like_count', 
            'comment_count', 'share_count', 'created_at', 'updated_at',
            'is_liked',   # ✅ you also forgot this one!
        ]
        read_only_fields = [
            'id', 'author', 'view_count', 'like_count', 
            'comment_count', 'share_count', 'created_at', 'updated_at'
        ]

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Like.objects.filter(
            user=request.user,
            post=obj   
        ).exists()
        return False


    def create(self, validated_data):
        tags_ids = validated_data.pop('tags_ids', [])
        post = Post.objects.create(**validated_data)
        if tags_ids:
            tags = Tag.objects.filter(id__in=tags_ids)
            post.tags.set(tags)
        return post

    def update(self, instance, validated_data):
        tags_ids = validated_data.pop('tags_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if tags_ids is not None:
            instance.tags.set(tags_ids)
        return instance

  
