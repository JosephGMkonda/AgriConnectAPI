from rest_framework import serializers
from .models import Post, Tag, Media
from django.contrib.auth import get_user_model
from Like.models import Like
from .services import upload_to_supabase

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = [
            'id', 'media_type', 'file_url', 'thumbnail_url',
            'alt_text', 'order', 'file_size', 'duration', 'created_at'
        ]
        read_only_fields = ['id', 'file_url', 'thumbnail_url', 'file_size', 'duration', 'created_at']


class PostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    media_files = MediaSerializer(many=True, read_only=True)

    media_uploads = serializers.ListField(
        child=serializers.FileField(max_length=100000, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False
    )

    tags_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
    )
    is_liked = serializers.SerializerMethodField()
    like_count_calc = serializers.IntegerField(read_only=True)
    comment_count_calc = serializers.IntegerField(read_only=True)

    class Meta:
        model = Post
        fields = [
            'id', 'author', 'title', 'content', 'post_type',
            'tags', 'tags_ids', 'media_files', 'media_uploads',
            'view_count', 'like_count_calc', 'comment_count_calc', 'share_count',
            'created_at', 'updated_at', 'is_liked',
        ]
        read_only_fields = [
            'id', 'author', 'view_count', 'like_count',
            'comment_count', 'share_count', 'created_at', 'updated_at'
        ]

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Like.objects.filter(user=request.user, post=obj).exists()
        return False

    def create(self, validated_data):
        media_files = validated_data.pop('media_uploads', [])
        tags_ids = validated_data.pop('tags_ids', [])
        post = Post.objects.create(**validated_data)

        
        if tags_ids:
            tags = Tag.objects.filter(id__in=tags_ids)
            post.tags.set(tags)

        
        if media_files:
            for index, file in enumerate(media_files):
                file_url, file_size, duration, thumbnail_url = upload_to_supabase(file)
                Media.objects.create(
                    post=post,
                    media_type="video" if "video" in file.content_type else "image",
                    file_url=file_url,
                    file_size=file_size,
                    duration=duration,
                    thumbnail_url=thumbnail_url,
                    order=index
                )
        return post

    def update(self, instance, validated_data):
        media_uploads = validated_data.pop('media_uploads', None)
        tags_ids = validated_data.pop('tags_ids', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if tags_ids is not None:
            instance.tags.set(tags_ids)

        if media_uploads:
            for index, file in enumerate(media_uploads):
                file_url, file_size, duration, thumbnail_url = upload_to_supabase(file)
                Media.objects.create(
                    post=instance,
                    media_type="video" if "video" in file.content_type else "image",
                    file_url=file_url,
                    file_size=file_size,
                    duration=duration,
                    thumbnail_url=thumbnail_url,
                    order=index
                )
        return instance
