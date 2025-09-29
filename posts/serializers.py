from rest_framework import serializers
from .models import Post, Tag, Media
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from .services import upload_to_supabase
from users.serializers import UserSerializer, AuthorProfileSerializer 
from Like.models import Like
from Like.serializers import LikeSerializer

from Comments.models import Comment 
from django.db.models import Max  


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
        read_only_fields = fields


class PostSerializer(serializers.ModelSerializer):
    author = AuthorProfileSerializer(read_only=True)
    media_files = MediaSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    tags_names = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False
    )
    media_uploads = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False
    )
    
    is_liked = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()  

    class Meta:
        model = Post
        fields = [
            'id', 'author', 'title', 'content', 'post_type',
            'tags', 'tags_names', 'media_files', 'media_uploads',
            'is_liked', 'comments_count',   
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Like.objects.filter(user=request.user, post=obj).exists()
        return False

    def get_comments_count(self, obj):
        return Comment.objects.filter(post=obj).count()   

    def create(self, validated_data):
        media_files = validated_data.pop('media_uploads', [])
        tags_names = validated_data.pop('tags_names', [])
        author = self.context['request'].user

        post = Post.objects.create(author=author, **validated_data)

        for tag_name in tags_names:
            tag, created = Tag.objects.get_or_create(
                name=tag_name,
                defaults={'slug': slugify(tag_name)}
            )
            post.tags.add(tag)

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
        media_files = validated_data.pop('media_uploads', [])
        tags_names = validated_data.pop('tags_names', [])
        
        request = self.context.get('request')
        media_to_remove = request.data.getlist('media_to_remove', [])
        existing_media_urls = request.data.getlist('existing_media_urls', [])
    
        
        
        
        
        
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.post_type = validated_data.get('post_type', instance.post_type)
        instance.save()
        
        if tags_names is not None:
            instance.tags.clear()
            for tag_name in tags_names:
                tag, created = Tag.objects.get_or_create(
                name=tag_name,
                defaults={'slug': slugify(tag_name)}
            )
            instance.tags.add(tag)
        if media_to_remove:
            Media.objects.filter(id__in=media_to_remove, post=instance).delete()
            
        urls_to_remove = set()
        if existing_media_urls:
            current_media_urls = set(instance.media_files.values_list('file_url', flat=True))
            keep_urls = set(existing_media_urls)
            urls_to_remove = current_media_urls - keep_urls
        if urls_to_remove:
            Media.objects.filter(file_url__in=urls_to_remove, post=instance).delete()
            

        if media_files:
            current_max_order = Media.objects.filter(post=instance).aggregate(Max('order'))['order__max'] or 0
        
            for index, file in enumerate(media_files):
                file_url, file_size, duration, thumbnail_url = upload_to_supabase(file)
                Media.objects.create(
                post=instance,
                media_type="video" if "video" in file.content_type else "image",
                file_url=file_url,
                file_size=file_size,
                duration=duration,
                thumbnail_url=thumbnail_url,
                order=current_max_order + index + 1)
            

        return instance
