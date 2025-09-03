from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    class Meta:
        model = User
        fields = ('id', 'supabase_uid', 'username', 'email', 'password', 'bio', 'avatar_url')
        extra_kwargs = {
            'supabase_uid': {'required': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
        
