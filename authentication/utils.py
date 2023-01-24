import datetime
import jwt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

from .models import UserToken

from innotter.settings import (
    REFRESH_PUBLIC,
    REFRESH_PHRASE,
)

from innotter.jwt_token_exceptions import (
    RefreshTokenExpired,
    RefreshTokenNotFound,
    InvalidRefreshToken,
)


def generate_jwt_token(user_id: int, priv_key, phrase, exp_days, exp_minutes) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.utcnow()
        + datetime.timedelta(days=exp_days, minutes=exp_minutes),
        "iat": datetime.datetime.utcnow(),
    }
    priv_key = serialization.load_pem_private_key(
        priv_key, phrase, backend=default_backend()
    )
    jwt_token = jwt.encode(payload, priv_key, algorithm="RS256")
    if phrase == REFRESH_PHRASE:
        user_token = UserToken(
            user_id=user_id,
            refresh_token=jwt_token,
            expires_at=payload["exp"],
            created_at=payload["iat"],
        )
        user_token.save()
    return jwt_token


def decode_refresh_token(refresh_token: str) -> dict:
    if not refresh_token:
        raise RefreshTokenNotFound

    try:
        payload = jwt.decode(refresh_token, REFRESH_PUBLIC, algorithms=["RS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise RefreshTokenExpired
    except (jwt.DecodeError, jwt.InvalidTokenError):
        raise InvalidRefreshToken
    
def update_valid_refresh_tokens_to_invalid(user_id: int):
    # Update all tokens, that are valid to invalid
    user_tokens = UserToken.objects.filter(user_id=user_id).filter(is_valid=True)
    for object in user_tokens:
        object.is_valid = False

    UserToken.objects.bulk_update(user_tokens, ["is_valid"])

