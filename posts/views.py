from rest_framework import viewsets, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Post, Tag
from rest_framework.response import Response
from .serializers import PostSerializer, TagSerializer
from .pagenation import OptimizedPagination
from users.authentication import SupabaseJWTAuthentication

from .permissions import IsAuthorOrReadOnly
from django.db.models import Count, Prefetch
from rest_framework.decorators import action
from Like.models import Like

class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    pagination_class = OptimizedPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    authentication_classes = [SupabaseJWTAuthentication]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        queryset = (
            Post.objects.select_related("author")
            .prefetch_related(
                Prefetch("tags", queryset=Tag.objects.only("id", "name", "slug"))
            )
            .annotate(
                like_count_calc=Count("likes", distinct=True),
                comment_count_calc=Count("comments", distinct=True),
            )
        )
    
        post_type = self.request.query_params.get("type")
        if post_type:
            queryset = queryset.filter(post_type=post_type)

        tag_slug = self.request.query_params.get("tag")
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)

        author_id = self.request.query_params.get("author")
        if author_id:
            queryset = queryset.filter(author_id=author_id)

        ordering = self.request.query_params.get("ordering", "-created_at")
        if ordering in ["created_at", "-created_at", "view_count", "-view_count", "like_count", "-like_count"]:
            queryset = queryset.order_by(ordering)

        return queryset

    def perform_create(self, serializer):
        
        serializer.save()


    @action(detail=True, methods=['post'], url_path='like')
    def like_post(self, request, pk=None):
        post = self.get_object()
        user = request.user

    
        like, created = Like.objects.get_or_create(user=user, post=post)
        if created:
            
            post.like_count += 1
            post.save(update_fields=['like_count'])
            return Response({'status': 'liked', 'like_count': post.like_count})
        else:
            
            like.delete()
            post.like_count -= 1
            post.save(update_fields=['like_count'])
            return Response({'status': 'unliked', 'like_count': post.like_count})