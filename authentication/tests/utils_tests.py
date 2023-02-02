import pytest
import jwt
import datetime


from authentication.services.jwt_token_generation import JwtTokenGenerationService
from authentication.models import UserToken

from django.conf import settings as sett


class TestJwtToken:
    def test_generation_of_access_token(self):
        access_token = JwtTokenGenerationService(1).generate_access_token()

        payload = jwt.decode(access_token, sett.ACCESS_PUBLIC_KEY, algorithms=["RS256"])
        assert payload["user_id"] == 1

    @pytest.mark.django_db
    def test_generation_of_refresh_token(self):
        refresh_token = JwtTokenGenerationService(1).generate_refresh_token()

        payload = jwt.decode(
            refresh_token, sett.REFRESH_PUBLIC_KEY, algorithms=["RS256"]
        )

        assert payload["user_id"] == 1

    @pytest.mark.django_db
    def test_generation_of_refresh_token_saves_new_UserToken_object(self):
        refresh_token = JwtTokenGenerationService(2).generate_refresh_token()
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
        refresh_token = JwtTokenGenerationService(-3).generate_refresh_token()

        user_token1 = UserToken.objects.filter(refresh_token="Some Token").first()
        user_token2 = UserToken.objects.filter(refresh_token=refresh_token).first()

        assert user_token1 and user_token1.is_valid == False
        assert user_token2 and user_token2.is_valid == True
