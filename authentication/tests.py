from django.test import TestCase

from accounts.models import User

from rest_framework.test import APIClient, APIRequestFactory
from rest_framework import exceptions

from innotter.settings import REFRESH_PRIVATE, REFRESH_PHRASE
import jwt
import datetime
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

from accounts.serializers import UserSerializer
from .views import AuthenticationView
from .models import UserToken


class AuthenticationLoginViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test_user", password="test_password", email="test@gmail.com"
        )
        self.client = APIClient()

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
        # хз как проверить то, что в куки возвращается refresh_token...


class AuthenticationRefreshViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test_user", password="test_password", email="test@gmail.com"
        )
        self.factory = APIRequestFactory()
        self.view = AuthenticationView()

    def create_request(self, user_id: int, invalid_ref_tok=None, is_valid=True) -> str:

        refresh_token, payload = self.create_refresh_token(user_id)

        self.update_user_token_table(
            user_id, refresh_token, payload, invalid_ref_tok, is_valid
        )
        request = self.factory.get("/api/v1/auth/refresh/", {})
        request.COOKIES["refreshtoken"] = refresh_token
        self.view.request = request
        return request

    def test_refresh_raises_user_not_found(self):
        request = self.create_request(-3)
        with self.assertRaisesRegex(
            exceptions.AuthenticationFailed,
            "User in refresh key not found. Please sign in again.",
        ):
            self.view.refresh(request)

    def test_refresh_raises_invalid_refresh_token(self):
        request = self.create_request(self.user.id, invalid_ref_tok="invalid token")
        with self.assertRaisesRegex(
            exceptions.AuthenticationFailed,
            "The Refresh Token is invalid. Please sign in again.",
        ):
            self.view.refresh(request)

    def test_refresh_raises_invalid_refresh_token_based_on_user_token(self):
        request = self.create_request(self.user.id, is_valid=False)
        with self.assertRaisesRegex(
            exceptions.AuthenticationFailed,
            "The refresh token is invalid, all refresh tokens of this user are deleted. Sign in again.",
        ):
            self.view.refresh(request)

    def test_refresh_returns_new_access_token(self):
        request = self.create_request(self.user.id)
        response = self.view.refresh(request)
        assert response.status_code == 200
        assert response.data["access_token"] != None
        assert response.data["user"] == UserSerializer(self.user).data
        assert response.data["expires_in"] != None
        assert response.data["token_type"] == "Bearer"
        # хз как проверить то, что в куки возвращается refresh_token...

    def create_refresh_token(self, user_id):
        payload = {
            "user_id": user_id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=0, minutes=30),
            "iat": datetime.datetime.utcnow(),
        }
        priv_key = serialization.load_pem_private_key(
            REFRESH_PRIVATE, REFRESH_PHRASE, backend=default_backend()
        )
        refresh_token = jwt.encode(payload, priv_key, algorithm="RS256")
        return refresh_token, payload

    def update_user_token_table(
        self, user_id, refresh_token, payload, invalid_ref_tok=None, is_valid=False
    ):
        u_t_refresh_token = refresh_token if not invalid_ref_tok else invalid_ref_tok
        UserToken.objects.all().delete()
        user_token = UserToken(
            user_id=user_id,
            refresh_token=u_t_refresh_token,
            expires_at=payload["exp"],
            created_at=payload["iat"],
            is_valid=is_valid,
        )
        user_token.save()
