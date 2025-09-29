from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny


from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .models import UserProfile
from .serializers import UserProfileCreateSerializer, UserProfileSerializer, UserProfileUpdateSerializer
from users.authentication import SupabaseJWTAuthentication
from posts.models import Post
from Follow.models import Follow
from Like.models import Like
from posts.serializers import PostSerializer
from Follow.serializers import followSerializer
from django.db.models import Count, Q, Case, When, Value, FloatField
from django.db.models.functions import Coalesce
from math import radians, sin, cos, sqrt, atan2
import random
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
    parser_classes,
)
from rest_framework.parsers import MultiPartParser, FormParser




User = get_user_model()


@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_profile(request):
    try:
        username = request.GET.get('username')
        if username:
            user = get_object_or_404(User, username=username)
        else:
            user = request.user
        
        
        profile = get_object_or_404(UserProfile, user=user)
        
        
        post_type = request.GET.get('type', '')
        posts = Post.objects.filter(author=user)
        
        if post_type and post_type in dict(Post.POST_TYPES).keys():
            posts = posts.filter(post_type=post_type)
        
        posts = posts.order_by('-created_at')
        
        
        post_counts = Post.objects.filter(author=user).values('post_type').annotate(
    count=Count('id')
)

        
        
        post_type_counts = {item['post_type']: item['count'] for item in post_counts}
        
        
        profile_serializer = UserProfileSerializer(profile)
        posts_serializer = PostSerializer(posts, many=True, context={'request': request})
        
        return Response({
            'profile': profile_serializer.data,
            'posts': posts_serializer.data,
            'post_count': posts.count(),
            'post_type_counts': post_type_counts,  
            'follower_count': 0,
            'following_count': 0,
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT', 'PATCH'])
@authentication_classes([SupabaseJWTAuthentication])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def update_user_profile(request):
    try:
      
        profile = get_object_or_404(UserProfile, user=request.user)
        

        data = request.data.copy()

        
         

            

        serializer = UserProfileUpdateSerializer(
            profile,
            data=data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(UserProfileSerializer(profile).data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view
@authentication_classes([SupabaseJWTAuthentication])

def search_profile(request):
    try:

        query = request.GET.get('q', '')
        if not query:
            return Response({'error': 'Search query required'}, status=status.HTTP_400_BAD_REQUEST)

        profiles = UserProfile.objects.filter(user__username__icontains=query)[:5]

        serializer = UserProfileSerializer(profiles, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def friend_recommendations(request):
    try:
        current_user = request.user
        current_profile = UserProfile.objects.get(user=current_user)
        
        
        followed_users = Follow.objects.filter(
            follower=current_user
        ).values_list('following_id', flat=True)
        
        
        exclude_ids = list(followed_users) + [current_user.id]
        
        
        potential_users = User.objects.exclude(id__in=exclude_ids)
        
        if not potential_users.exists():
            return Response({'suggested_users': [], 'already_following': []})
        
        
        user_scores = []
        for user in potential_users:
            try:
                user_profile = UserProfile.objects.get(user=user)
                score = calculate_user_score(current_user, current_profile, user, user_profile)
                user_scores.append((user, score, user_profile))
            except UserProfile.DoesNotExist:
                continue
        
        
        user_scores.sort(key=lambda x: x[1], reverse=True)
        top_users = [user_scores[i] for i in range(min(20, len(user_scores)))]
        
    
        following_users = Follow.objects.filter(
            follower=current_user
        ).select_related('following', 'following__userprofile')[:50]
        
        
        suggested_serializer = UserProfileSerializer(
            [score[2] for score in top_users], 
            many=True,
            context={'current_user': current_user}
        )
        
        following_serializer = followSerializer(following_users, many=True)
        
        return Response({
            'suggested_users': suggested_serializer.data,
            'already_following': following_serializer.data
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    """
    Calculate recommendation score based on multiple factors
    Returns a score between 0-100
    """

def calculate_user_score(current_user, current_profile, target_user, target_profile):
    
    total_score = 0
    max_possible = 0
    
    
    if current_profile.farmType and target_profile.farmType:
        farm_weight = 40
        if current_profile.farmType.lower() == target_profile.farmType.lower():
            total_score += farm_weight
        max_possible += farm_weight
    
    
    post_weight = 25
    post_score = calculate_post_type_similarity(current_user, target_user)
    total_score += post_score * (post_weight / 100)
    max_possible += post_weight
    
    
    location_weight = 20
    location_score = calculate_location_similarity(current_profile, target_profile)
    total_score += location_score * (location_weight / 100)
    max_possible += location_weight
    
    
    engagement_weight = 10
    engagement_score = calculate_engagement_similarity(current_user, target_user)
    total_score += engagement_score * (engagement_weight / 100)
    max_possible += engagement_weight
    
    
    random_weight = 5
    total_score += random.uniform(0, random_weight)
    max_possible += random_weight
    
    
    if max_possible > 0:
        return (total_score / max_possible) * 100
    return random.uniform(0, 30) 

    """
    Calculate similarity based on post types they interact with
    """ 

def calculate_post_type_similarity(current_user, target_user):
    
    
    current_user_posts = Post.objects.filter(author=current_user)
    current_user_likes = Like.objects.filter(user=current_user).select_related('post')
    
    current_post_types = list(current_user_posts.values_list('post_type', flat=True))
    current_liked_types = [like.post.post_type for like in current_user_likes]
    
    all_current_types = current_post_types + current_liked_types
    current_type_counts = {pt: all_current_types.count(pt) for pt in set(all_current_types)}
    
    
    target_posts = Post.objects.filter(author=target_user)
    target_types = list(target_posts.values_list('post_type', flat=True))
    target_type_counts = {pt: target_types.count(pt) for pt in set(target_types)}
    
    
    intersection = set(current_type_counts.keys()) & set(target_type_counts.keys())
    union = set(current_type_counts.keys()) | set(target_type_counts.keys())
    
    if not union:
        return 0
    
    return (len(intersection) / len(union)) * 100

def calculate_location_similarity(current_profile, target_profile):
    
    if current_profile.location and target_profile.location:
        if current_profile.location.lower() == target_profile.location.lower():
            return 100
        
    return 0

def calculate_engagement_similarity(current_user, target_user):
    
    current_liked_posts = set(Like.objects.filter(user=current_user).values_list('post_id', flat=True))
    target_liked_posts = set(Like.objects.filter(user=target_user).values_list('post_id', flat=True))
    
    common_likes = current_liked_posts & target_liked_posts
    
    if not current_liked_posts or not target_liked_posts:
        return 0
    
    return (len(common_likes) / len(current_liked_posts | target_liked_posts)) * 100