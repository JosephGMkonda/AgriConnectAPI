from rest_framework import viewsets, permissions, mixins, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Follow
from .serializers import followSerializer


User = get_user_model()


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all().select_related("follower","following")
    serializer_class = followSerializer
    permission_class = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        follower_id = self.request.query_params.get("follower")
        following_id = self.request.query_params.get("following")

        if follower_id:
            queryset = queryset.filter(follower_id=follower_id)

        if following_id:
            queryset = queryset.filter(following_id=following_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(follower=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.follower != request.user:
            return Response({"detail":"You can not follow on behalf of another user"},
            status = status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return Response({"detail":"Unfollowed successfully"}, status=status.HTTP_204_NO_CONTENT)
