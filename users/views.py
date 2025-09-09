from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .serializers import UserSerializer
from Userprofile.serializers import UserProfileSerializer
from Userprofile.models import UserProfile
from django.views.decorators.csrf import csrf_exempt
from .authentication import SupabaseJWTAuthentication
import logging
import jwt
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

User = get_user_model()


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@csrf_exempt
def create_user(request):
    logger.info(f"Received request: {request.data}")
    
    try:
        
        required_fields = ['supabase_uid', 'username', 'email']
        for field in required_fields:
            if field not in request.data:
                logger.error(f"Missing field: {field}")
                return Response(
                    {'error': f'Missing required field: {field}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        
        if User.objects.filter(supabase_uid=request.data['supabase_uid']).exists():
            logger.error(f"User already exists with UID: {request.data['supabase_uid']}")
            return Response(
                {'error': 'User already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            logger.info(f"User created: {user.username}")
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        
        logger.error(f"Serializer errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR

        )




@api_view(['GET'])
def list_users(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@authentication_classes([SupabaseJWTAuthentication])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    try:
        profile = get_object_or_404(UserProfile, user=request.user)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


