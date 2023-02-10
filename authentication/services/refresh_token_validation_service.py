from rest_framework import serializers

from authentication.models import UserToken
from accounts.models import User
from exceptions.jwt_token_exceptions import (
    RefreshTokenIsOld,
    RefreshTokenNotFound,
    InvalidRefreshToken,
    UserInRefreshTokenNotFound,
)


class RefreshTokenValidationService:
    def __init__(self, request):
        self.refresh_token = request.headers.get("Refresh-Token")

    def validate(self):
        if not self.refresh_token:
            raise RefreshTokenNotFound

        user_token = UserToken.objects.filter(refresh_token=self.refresh_token).first()
        if not user_token:
            raise InvalidRefreshToken

        if not user_token.is_valid:
            UserToken.objects.filter(user_id=user_token.user_id).delete()
            raise RefreshTokenIsOld

        user = User.objects.filter(id=user_token.user_id).first()
        if not user:
            UserToken.objects.filter(user_id=user_token.user_id).delete()
            raise UserInRefreshTokenNotFound

        self.user_id = user_token.user_id

    def get_validated_user_id(self) -> int:
        if self.user_id:
            return self.user_id
        msg = {"user_id": "Received refresh_token not validated yet."}
        raise serializers.ValidationError(msg, code="authorization")
