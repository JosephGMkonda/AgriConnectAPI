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
from posts.serializers import PostSerializer
from django.db.models import Count



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
def update_user_profile(request):
    try:
        profile = get_object_or_404(UserProfile, user=request.user)

        if request.method in ['PUT', 'PATCH']:
            serializer = UserProfileUpdateSerializer(
                profile,
                data = request.data,
                partial = request.method == 'PATCH'
            )

            if serializer.is_valid():
                serializer.save()
                return Response(UserProfileSerializer(profile).data)
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