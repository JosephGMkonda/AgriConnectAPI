import jwt
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from django.contrib.auth import get_user_model

User = get_user_model()

class SupabaseJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return None  

        token = auth_header.split(" ")[1]

        try:
            
            payload = jwt.decode(
                token,
                options={"verify_signature": False},  
                algorithms=["HS256"]
            )
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("Token expired")
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed("Invalid token")

        
        email = payload.get("email")
        if not email:
            raise exceptions.AuthenticationFailed("No email in token")

        
        user, _ = User.objects.get_or_create(email=email, defaults={"username": email})

        return (user, None)
