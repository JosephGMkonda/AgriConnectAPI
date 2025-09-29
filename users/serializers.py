from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from Userprofile.models import UserProfile

User = get_user_model()

class AuthorProfileSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()
    bio = serializers.SerializerMethodField()
    farmType = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'avatar_url', 'bio', 'farmType')
    def get_avatar_url(self, obj):
        try:
            return obj.userprofile.avatar_url
        except UserProfile.DoesNotExist:
            return None
    def get_farmType(self, obj):
        try:
            return obj.userprofile.farmType
        except UserProfile.DoesNotExist:
            return None
    def get_bio(self, obj):
        try:
            return obj.userprofile.bio
        except UserProfile.DoesNotExist:
            return None


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'supabase_uid', 'username', 'email')
        extra_kwargs = {
            'supabase_uid': {'required': True},
            'username': {'required': True},
            'email': {'required': True},
        }

    def create(self, validated_data):
        
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            supabase_uid=validated_data['supabase_uid']
        )
        return user