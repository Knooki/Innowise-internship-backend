import jwt
import re

from django.conf import settings

from rest_framework import authentication

from .services.user_validation_service import validate_user_service


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

        payload = jwt.decode(
            access_token, settings.ACCESS_PUBLIC_KEY, algorithms=["RS256"]
        )

        user = validate_user_service(payload["user_id"])
        return (user, access_token)
