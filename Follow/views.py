from rest_framework import viewsets, permissions, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response

from django.contrib.auth import get_user_model
from django.db.models import Count

from .models import Follow
from .serializers import followSerializer

User = get_user_model()


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all().select_related("follower", "following")
    serializer_class = followSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Follow.objects.filter(follower=self.request.user).select_related("follower", "following")

        following_id = self.request.query_params.get("following")
        if following_id:
            queryset = queryset.filter(following_id=following_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(follower=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.follower != request.user:
            return Response(
                {"detail": "You can not unfollow on behalf of another user"},
                status=status.HTTP_403_FORBIDDEN,
            )
        self.perform_destroy(instance)
        return Response(
            {"detail": "Unfollowed successfully"}, status=status.HTTP_204_NO_CONTENT
        )

    
    @action(detail=False, methods=["get"], url_path="suggested")
    def suggested_users(self, request):
        user = request.user

        
        following_ids = Follow.objects.filter(follower=user).values_list("following_id", flat=True)

    
        queryset = (
            User.objects.exclude(id=user.id)
            .exclude(id__in=following_ids)
            .annotate(follower_count=Count("followers"))
            .order_by("-follower_count")[:10]  
        )

    
        data = [
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "avatar_url": getattr(u, "avatar_url", None),
                "follower_count": u.follower_count,
            }
            for u in queryset
        ]

        return Response(data, status=status.HTTP_200_OK)

