from rest_framework import viewsets,permissions
from .serializer import CommentSerializer
from .models import Comment
from posts.permissions import IsAuthorOrReadOnly


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.filter(is_active=True).select_related("author","post")
    serializer_class = CommentSerializer
    permission_class = [permissions.IsAuthorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
