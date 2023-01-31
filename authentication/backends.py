import jwt
import re

from django.conf import settings

from rest_framework import authentication, exceptions

from accounts.models import User


class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        request.user = None

        if any(
            re.fullmatch(pattern, request.path)
            for pattern in settings.JWT_UNAUTHENTICATED_URL_PATTERNS
        ):
            return None

        auth_header = authentication.get_authorization_header(request).split()
        access_token = auth_header[1].decode("utf-8")

        return self._authenticate_credentials(request, access_token)

    def _authenticate_credentials(self, request, token):
        payload = jwt.decode(
            token, settings.ACCESS_PUBLIC_KEY, algorithms=["RS256"]
        )

        try:
            user = User.objects.get(pk=payload["user_id"])
        except User.DoesNotExist:
            msg = "User in given token not found."
            raise exceptions.AuthenticationFailed(msg)

        if not user.is_active:
            msg = "Given user is deactivated."
            raise exceptions.AuthenticationFailed(msg)

        if user.is_blocked:
            msg = "Given user is blocked."
            raise exceptions.AuthenticationFailed(msg)

        return (user, token)
