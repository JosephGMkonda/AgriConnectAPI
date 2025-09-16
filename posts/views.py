from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Count, Prefetch
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django.shortcuts import get_object_or_404

from .models import Post, Tag
from Comments.models import Comment
from Like.models import Like
from .serializers import PostSerializer, TagSerializer
from .pagenation import OptimizedPagination
from users.authentication import SupabaseJWTAuthentication
from .permissions import IsAuthorOrReadOnly


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    pagination_class = OptimizedPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    authentication_classes = [SupabaseJWTAuthentication]

    def get_queryset(self):
        queryset = (
            Post.objects.select_related("author")
            .prefetch_related(
                Prefetch("tags", queryset=Tag.objects.only("id", "name", "slug")),
                Prefetch(
                    "comments",
                    queryset=Comment.objects.filter(is_active=True).select_related("author"),
                ),
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
        if ordering in [
            "created_at",
            "-created_at",
            "view_count",
            "-view_count",
            "like_count",
            "-like_count",
        ]:
            queryset = queryset.order_by(ordering)

        return queryset

    @method_decorator(cache_page(60 * 2))
    @method_decorator(vary_on_cookie)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["post"])
    def like(self, request, pk=None):
        post = self.get_object()
        like, created = Like.objects.get_or_create(
            user=request.user,
            post=post,  
        )

        if created:
            post.like_count += 1
            post.save(update_fields=["like_count"])
            return Response({"status": "liked"})
        else:
            like.delete()
            post.like_count -= 1
            post.save(update_fields=["like_count"])
            return Response({"status": "unliked"})

    @action(detail=True, methods=["post"])
    def increment_views(self, request, pk=None):
        post = self.get_object()
        post.increment_view_count()
        return Response({"status": "view count incremented"})


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
