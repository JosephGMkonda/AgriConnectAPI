from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model
from .serializers import UserSerializer


User = get_user_model()


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def create_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def list_users(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def retrieve_user(request, pk):
    user = User.objects.get(pk=pk)
    serializer = UserSerializer(user)
    return Response(serializer.data)