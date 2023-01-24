import jwt
import re

from django.utils.deprecation import MiddlewareMixin

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
            raise AccessTokenNotFound

        if not re.fullmatch(REGEX_BEARER, authorization_header_value):
            raise BearerKeywordNotFound
        try:
            access_token = authorization_header_value.split(" ")[-1]
            print(access_token)
            payload = jwt.decode(access_token, ACCESS_PUBLIC, algorithms=["RS256"])
            return None
        except jwt.ExpiredSignatureError:
            raise AccessTokenExpired
        except (jwt.DecodeError, jwt.InvalidTokenError):
            raise InvalidAccessToken
