from rest_framework import serializers
from .models import Follow
from django.contrib.auth import get_user_model


User = get_user_model()

class followSerializer(serializers.ModelSerializer):
    follower_name = serializers.CharField(source="follower.username", read_only=True)
    following_name = serializers.CharField(source="following.username", read_only=True)

    class Meta:
        models = Follow
        fields =['id','follower','follower_name','following','following_name','created_at']
        read_only_fields=['follower','created_at']

    def validate(self, data):
        request_user = self.context["request"].user
        following = data.get("following")

        if request_user == following:
            raise serializers.ValidationError("you can not follow yourself")

        if Follow.objects.filter(follower=request_user, following=following).exists():
            raise serializers.ValidationError("You already follow this user")

        return data
    def create(self, validated_data):
        validated_data["follower"] = self.context["request"].user
        return super().create(validated_data)

