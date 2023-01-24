from django.test import TestCase

from django.contrib.auth import get_user_model

from rest_framework.test import APIClient

from innotter.settings import ACCESS_PRIVATE, ACCESS_PHRASE
import jwt
import datetime
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

from accounts.serializers import UserSerializer


class AuthenticationViews(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="test_user", password="test_password", email="test@gmail.com"
        )
        self.client = APIClient()
        # access_token = self.create_access_token(self.user.id)
        # self.client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token)

    def create_access_token(self, user_id):
        payload = {
            "user_id": user_id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=0, minutes=30),
            "iat": datetime.datetime.utcnow(),
        }
        priv_key = serialization.load_pem_private_key(
            ACCESS_PRIVATE, ACCESS_PHRASE, backend=default_backend()
        )
        access_token = jwt.encode(payload, priv_key, algorithm="RS256")
        return access_token

    def test_login_returns_username_and_password_required(self):
        response = self.client.post("/api/v1/auth/login/", {}, format="json")

        assert response.status_code == 403
        assert response.data == {"detail": "username and password required"}

    def test_login_returns_user_not_found(self):
        response = self.client.post(
            "/api/v1/auth/login/",
            {"username": "wrong_user", "password": "wrong_password"},
        )
        assert response.status_code == 403
        assert response.data == {"detail": "user not found"}

    def test_login_returns_wrong_password(self):
        response = self.client.post(
            "/api/v1/auth/login/",
            {"username": "test_user", "password": "wrong_password"},
        )
        assert response.status_code == 403
        assert response.data == {"detail": "wrong password"}

    def test_login_authenticates_user(self):
        response = self.client.post(
            "/api/v1/auth/login/",
            {"username": "test_user", "password": "test_password"},
        )
        assert response.status_code == 200
        assert response.data["access_token"] != None
        assert response.data["user"] == UserSerializer(self.user).data
        assert response.data["expires_in"] != None
        assert response.data["token_type"] == "Bearer"
        assert response.COOKIES.get('refreshtoken') != None