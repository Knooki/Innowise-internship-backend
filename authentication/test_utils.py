import pytest
import jwt

from .utils import generate_jwt_token

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
    @pytest.makr.django_db
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

    