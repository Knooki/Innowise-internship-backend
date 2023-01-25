import jwt
from accounts.models import User
from rest_framework import exceptions

from .models import UserToken

from innotter.settings import (
    REFRESH_PUBLIC,
    ACCESS_PUBLIC,
)

from innotter.jwt_token_exceptions import (
    RefreshTokenExpired,
    RefreshTokenNotFound,
    InvalidRefreshToken,
)


class JwtTokenValidation:
    def __init__(self, jwt_token: str):
        self.jwt_token = jwt_token

    def validate_refresh_token(self) -> User:

        if not self.jwt_token:
            raise RefreshTokenNotFound

        user_id = self._decode_refresh_token()

        user = self._check_if_user_exists_in_db(user_id)

        self._check_if_refresh_token_exists_in_db_and_valid(user.id)

        return user

    def validate_access_token(self) -> User:
        user_id = jwt.decode(self.jwt_token, ACCESS_PUBLIC, algorithms=["RS256"])[
            "user_id"
        ]

        user = self._check_if_user_exists_in_db(user_id)

        return user

    def _decode_refresh_token(self) -> int:

        try:
            user_id = jwt.decode(self.jwt_token, REFRESH_PUBLIC, algorithms=["RS256"])[
                "user_id"
            ]

            return user_id

        except jwt.ExpiredSignatureError:
            raise RefreshTokenExpired

        except (jwt.DecodeError, jwt.InvalidTokenError):
            raise InvalidRefreshToken

    def _check_if_user_exists_in_db(self, user_id: int) -> User:

        user = User.objects.filter(id=user_id).first()

        if user is None:

            raise exceptions.AuthenticationFailed(
                "User in refresh key not found. Please sign in again."
            )

        return user

    def _check_if_refresh_token_exists_in_db_and_valid(self, user_id: int):

        user_token = UserToken.objects.filter(refresh_token=self.jwt_token)

        if not user_token:

            UserToken.objects.filter(user_id=user_id).delete()

            raise exceptions.AuthenticationFailed(
                "The Refresh Token is invalid. Please sign in again."
            )

        user_token = user_token.first()

        # If refresh_token is old
        if not user_token.is_valid:

            UserToken.objects.filter(user_id=user_id).delete()

            raise exceptions.AuthenticationFailed(
                "The refresh token is invalid, all refresh tokens of this user are deleted. Sign in again."
            )

        # make current token old
        user_token.is_valid = False
        user_token.save()
