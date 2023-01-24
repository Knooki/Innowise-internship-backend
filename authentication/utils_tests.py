import pytest
import jwt
import datetime

from .utils import generate_jwt_token, update_valid_refresh_tokens_to_invalid

from .models import UserToken

from innotter.settings import (
    ACCESS_PUBLIC,
    ACCESS_PRIVATE,
    ACCESS_PHRASE,
    ACCESS_EXP_M,
    REFRESH_PUBLIC,
    REFRESH_PRIVATE,
    REFRESH_PHRASE,
    REFRESH_EXP_D,
)


class TestAccessToken:
    def test_generation_of_access_token(self):
        access_token = generate_jwt_token(
            1, ACCESS_PRIVATE, ACCESS_PHRASE, 0, ACCESS_EXP_M
        )
        payload = jwt.decode(access_token, ACCESS_PUBLIC, algorithms=["RS256"])
        assert payload["user_id"] == 1

    @pytest.mark.django_db
    def test_generation_of_refresh_token(self):
        refresh_token = generate_jwt_token(
            1, REFRESH_PRIVATE, REFRESH_PHRASE, REFRESH_EXP_D, 0
        )

        payload = jwt.decode(refresh_token, REFRESH_PUBLIC, algorithms=["RS256"])

        assert payload["user_id"] == 1

    @pytest.mark.django_db
    def test_generation_of_refresh_token_saves_new_UserToken_object(self):
        refresh_token = generate_jwt_token(
            1, REFRESH_PRIVATE, REFRESH_PHRASE, REFRESH_EXP_D, 0
        )
        user_token = UserToken.objects.filter(refresh_token=refresh_token).get()
        assert user_token and user_token.is_valid == True

    @pytest.mark.django_db
    def test_updating_valid_refresh_tokens_to_invalid(self):
        UserToken.objects.create(
            user_id=-3,
            refresh_token="Some Token",
            expires_at=datetime.datetime.utcnow()
            + datetime.timedelta(days=0, minutes=2),
            created_at=datetime.datetime.utcnow(),
        )
        update_valid_refresh_tokens_to_invalid(-3)
        user_token = UserToken.objects.filter(user_id=-3).first()
        assert user_token.is_valid == False
