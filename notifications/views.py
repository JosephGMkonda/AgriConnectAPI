from rest_framework import viewsets, permissions
from .models import Notification
from .serializers import NotificationSerializer
from rest_framework.decorators import action
from rest_framework.response import Response

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.notifications.all()

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        count = self.request.user.notifications.filter(read=False).count()
        return Response({"unread_count": count})

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.read = True
        notification.save(update_fields=['read'])
        return Response({"status": "marked as read"})
