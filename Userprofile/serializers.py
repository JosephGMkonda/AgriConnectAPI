from .models import UserProfile
from rest_framework import serializers
from django.contrib.auth import get_user_model
from Follow.models  import Follow
from .service import upload_profile_avatar

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'email', 'bio', 'avatar_url',
        'phone_number', 'farmType', 'location', 'profile_completed','created_at', 'updated_at']
        read_only_fields = ['id','profile_completed', 'created_at', 'updated_at']

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    avatar_upload = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model = UserProfile
        fields = ['bio', 'avatar_url', 'avatar_upload', 'phone_number', 'farmType', 'location']

    def validate_avatar_url(self, value):
        if not value.startswith('https://ifqvnzunszqcrcllmejq.supabase.co/storage/'):
            raise serializers.ValidationError("Avatar URL must be from Supabase storage.")
            return value
    def update(self, instance, validated_data):
        avatar_file = validated_data.pop('avatar_upload', None)
        if avatar_file:
            file_url, _ = upload_profile_avatar(avatar_file)
            validated_data['avatar_url'] = file_url

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.profile_completed = True
        instance.save()
        return instance



class UserProfileCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['bio', 'avatar_url', 'phone_number', 'farmType', 'location']



class UserRecommendationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    email = serializers.EmailField(source='user.email')
    score = serializers.SerializerMethodField()
    common_interests = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'email', 'bio', 'avatar_url', 
                 'phone_number', 'farmType', 'location', 'score', 'common_interests']
    
    def get_score(self, obj):
        
        return self.context.get('user_scores', {}).get(obj.user.id, 0)
    
    def get_common_interests(self, obj):
        current_user = self.context.get('current_user')
        if not current_user:
            return []
        
        
        current_profile = UserProfile.objects.get(user=current_user)
        common = []
        
        if current_profile.farmType and obj.farmType and current_profile.farmType == obj.farmType:
            common.append(f"Same farming type: {current_profile.farmType}")
        
        
        
        return common[:3]  
        