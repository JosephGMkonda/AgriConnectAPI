from rest_framework import viewsets,permissions
from .serializer import CommentSerializer
from .models import Comment
from .permissions import IsAuthorOrReadOnly


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.filter(is_active=True).select_related("author","post")
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_queryset(self):
        queryset = Comment.objects.filter(is_active=True).select_related("author", "post")
        post_id = self.request.query_params.get('post')
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
