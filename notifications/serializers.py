from rest_framework import serializers
from .models import Notification
from users.serializers import UserSerializer, AuthorProfileSerializer

class NotificationSerializer(serializers.ModelSerializer):
    sender = AuthorProfileSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = '__all__'
        
