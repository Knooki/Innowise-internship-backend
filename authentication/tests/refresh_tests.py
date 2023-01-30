from django.test import TestCase

from accounts.models import User

from django.conf import settings
import jwt
import datetime
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

from authentication.models import UserToken


from rest_framework.test import APIClient


class AuthenticationRefreshViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test_user", password="test_password", email="test@gmail.com"
        )
        self.client = APIClient()

    def test_refresh_return_refresh_token_required(self):
        response = self.client.get("/api/v1/auth/refresh/", format="json")
        assert response.status_code == 400
        assert response.data == {
            "detail": "Refresh Token not found. Please put it in header named 'Refresh-Token'"
        }

    def test_refresh_raises_user_not_found(self):
        refresh_token = self.create_refresh_token(-3)

        self.client.credentials(HTTP_REFRESH_TOKEN=refresh_token)
        response = self.client.get("/api/v1/auth/refresh/", format="json")
        assert response.status_code == 400
        assert response.data == {
            "detail": "User in this refresh token doesn't exist anymore"
        }

    def test_refresh_raises_invalid_refresh_token(self):
        refresh_token = "invalid refresh token"

        self.client.credentials(HTTP_REFRESH_TOKEN=refresh_token)
        response = self.client.get("/api/v1/auth/refresh/", {}, format="json")
        assert response.status_code == 400
        assert response.data == {
            "detail": "No such Refresh Token in database. Please log in again."
        }

    def test_refresh_raises_invalid_refresh_token_based_on_user_token(self):
        refresh_token = self.create_refresh_token(self.user.id, is_valid=False)

        self.client.credentials(HTTP_REFRESH_TOKEN=refresh_token)
        response = self.client.get("/api/v1/auth/refresh/", {}, format="json")
        assert response.status_code == 400
        assert response.data == {
            "detail": "This refresh token is old. All refresh tokens of this user deleted. Please login again"
        }

    def test_refresh_returns_new_access_token(self):
        refresh_token = self.create_refresh_token(self.user.id)

        self.client.credentials(HTTP_REFRESH_TOKEN=refresh_token)
        response = self.client.get("/api/v1/auth/refresh/", {}, format="json")

        assert response.status_code == 200
        assert response.data["refresh_token"] != None
        assert response.data["access_token"] != None
        assert response.data["expires_in"] != None
        assert response.data["token_type"] == "Bearer"

    def create_refresh_token(self, user_id, is_valid=True):
        payload = {
            "user_id": user_id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=0, minutes=30),
            "iat": datetime.datetime.utcnow(),
        }
        priv_key = serialization.load_pem_private_key(
            settings.REFRESH_PRIVATE_KEY,
            settings.REFRESH_PASSPHRASE,
            backend=default_backend(),
        )
        refresh_token = jwt.encode(payload, priv_key, algorithm="RS256")
        self.update_user_token_table(user_id, refresh_token, payload, is_valid=is_valid)
        return refresh_token

    def update_user_token_table(self, user_id, refresh_token, payload, is_valid):
        user_tokens = UserToken.objects.filter(user_id=user_id)
        for object in user_tokens:
            object.is_valid = False
        UserToken.objects.bulk_update(user_tokens, ["is_valid"])

        user_token = UserToken(
            user_id=user_id,
            refresh_token=refresh_token,
            expires_at=payload["exp"],
            created_at=payload["iat"],
            is_valid=is_valid,
        )
        user_token.save()
