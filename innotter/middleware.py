import jwt
import re

from django.utils.deprecation import MiddlewareMixin
from exceptions.utils import create_exception_response

from exceptions.jwt_token_exceptions import (
    AccessTokenExpired,
    InvalidAccessToken,
    AccessTokenNotFound,
    BearerKeywordNotFound,
)

from django.conf import settings


class JWTMiddleware(MiddlewareMixin):
    def process_request(self, request):

        if any(
            re.fullmatch(pattern, request.path)
            for pattern in settings.JWT_UNAUTHENTICATED_URL_PATTERNS
        ):
            return None

        # Authorization: Bearer xxxxxxxxxxxxxxx
        authorization_header_value = request.headers.get("Authorization")

        if not authorization_header_value:
            raise (AccessTokenNotFound)

        if not re.fullmatch(settings.REGEX_BEARER, authorization_header_value):
            raise (BearerKeywordNotFound)
        try:
            access_token = authorization_header_value.split(" ")[-1]
            payload = jwt.decode(
                access_token, settings.ACCESS_PUBLIC_KEY, algorithms=["RS256"]
            )
            return None
        except jwt.ExpiredSignatureError:
            raise (AccessTokenExpired)
        except (jwt.DecodeError, jwt.InvalidTokenError):
            raise (InvalidAccessToken)
