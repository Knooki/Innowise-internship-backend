import datetime
import jwt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization


from ..models import UserToken

from django.conf import settings


class JwtTokenGenerationService:
    def __init__(self, user_id: int):
        self.user_id = user_id

    def generate_data_for_response(self) -> dict:
        access_token = self.generate_access_token()
        refresh_token = self.generate_refresh_token()
        data = {
            "refresh_token": refresh_token,
            "access_token": access_token,
            "expires_in": settings.ACCESS_EXPIRES_IN_MINUTES * 60,
            "token_type": "Bearer",
        }

        return data

    def generate_access_token(self):
        payload = {
            "user_id": self.user_id,
            "exp": datetime.datetime.utcnow()
            + datetime.timedelta(days=0, minutes=settings.ACCESS_EXPIRES_IN_MINUTES),
            "iat": datetime.datetime.utcnow(),
        }
        priv_key = serialization.load_pem_private_key(
            settings.ACCESS_PRIVATE_KEY,
            settings.ACCESS_PASSPHRASE,
            backend=default_backend(),
        )
        jwt_token = jwt.encode(payload, priv_key, algorithm="RS256")
        return jwt_token

    def generate_refresh_token(self):
        payload = {
            "user_id": self.user_id,
            "exp": datetime.datetime.utcnow()
            + datetime.timedelta(days=settings.REFRESH_EXPIRES_IN_DAYS, minutes=0),
            "iat": datetime.datetime.utcnow(),
        }
        priv_key = serialization.load_pem_private_key(
            settings.REFRESH_PRIVATE_KEY,
            settings.REFRESH_PASSPHRASE,
            backend=default_backend(),
        )
        jwt_token = jwt.encode(payload, priv_key, algorithm="RS256")
        self._update_valid_refresh_tokens_to_invalid()
        user_token = UserToken(
            user_id=self.user_id,
            refresh_token=jwt_token,
            expires_at=payload["exp"],
            created_at=payload["iat"],
        )
        user_token.save()
        return jwt_token

    def _update_valid_refresh_tokens_to_invalid(self):
        # Update all tokens, that are valid to invalid
        user_tokens = UserToken.objects.filter(user_id=self.user_id).filter(
            is_valid=True
        )
        for object in user_tokens:
            object.is_valid = False

        UserToken.objects.bulk_update(user_tokens, ["is_valid"])
