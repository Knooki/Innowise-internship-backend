import jwt
import re

from django.utils.deprecation import MiddlewareMixin
from innotter.utils import create_exception_response

from .jwt_token_exceptions import (
    AccessTokenExpired,
    InvalidAccessToken,
    AccessTokenNotFound,
    BearerKeywordNotFound,
)

from innotter.settings import (
    ACCESS_PUBLIC,
    JWT_UNAUTHENTICATED_URL_PATTERNS,
    REGEX_BEARER,
)


class JWTMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # if user is not authenticated
        # now it is ["/", "/admin/.+"]
        if any(
            re.fullmatch(pattern, request.path)
            for pattern in JWT_UNAUTHENTICATED_URL_PATTERNS
        ):
            return None

        # Authorization: Bearer xxxxxxxxxxxxxxx
        authorization_header_value = request.headers.get("Authorization")

        if not authorization_header_value:
            return create_exception_response(AccessTokenNotFound)

        if not re.fullmatch(REGEX_BEARER, authorization_header_value):
            return create_exception_response(BearerKeywordNotFound)
        try:
            access_token = authorization_header_value.split(" ")[-1]
            payload = jwt.decode(access_token, ACCESS_PUBLIC, algorithms=["RS256"])
            return None
        except jwt.ExpiredSignatureError:
            return create_exception_response(AccessTokenExpired)
        except (jwt.DecodeError, jwt.InvalidTokenError):
            return create_exception_response(InvalidAccessToken)
