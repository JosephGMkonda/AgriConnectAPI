from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()



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