from rest_framework import serializers
from .models import Notification
from users.serializers import UserSerializer  

class NotificationSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'recipient', 'sender', 'notif_type', 'message', 'link', 'read', 'created_at']
        read_only_fields = ['id', 'created_at', 'sender']
