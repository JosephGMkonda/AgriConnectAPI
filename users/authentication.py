import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import authentication, exceptions
from rest_framework.exceptions import AuthenticationFailed


User = get_user_model()

class supabaseJwtAuthentication(authentication.BaseAuthentication):
    keyword = 'Bearer'

    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return None

        try:

            token = auth_header.split(' ')[1]
        except IndexError:
            raise AuthenticationFailed('Bearer token not found')

        try:
            payload = jwt.decode(
                token, 
                settings.SUPABASE_ANON_KEY,
                 algorithms=['HS256'],
                 audience='authenticated',
                 options={"verify_iss": False}
                 )

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token')

        supabase_uid = payload.get('sub')
        if not supabase_uid:
            raise AuthenticationFailed('Token contained no user id (sub).')
        try:
            user = User.objects.get(supabase_uid=supabase_uid)
        except User.DoesNotExist:
            email = payload.get('email')
            username = email.split('@')[0] 
            user = User.objects.create_user(
                username=username,
                email=email,
                supabase_uid=supabase_uid
            )

        return (user, token)