import jwt
import datetime
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from django.conf import settings

from django.test import TestCase

from accounts.models import User

from rest_framework import exceptions

from rest_framework.test import APIRequestFactory


from authentication.backends import JWTAuthentication


class AuthenticationLoginViewTestCase(TestCase):
    def setUp(self):
        self.not_active_user = User.objects.create_user(
            username="not_active_user",
            password="test_password",
            email="not.active@gmail.com",
            is_active=False,
        )
        self.blocked_user = User.objects.create_user(
            username="blocked_user",
            password="test_password",
            email="blocked@gmail.com",
            is_blocked=True,
        )
        self.valid_user = User.objects.create_user(
            username="test_user", password="test_password", email="test@gmail.com"
        )
        self.factory = APIRequestFactory()

    def test_backend_returns_null_if_unauthenticated_url_patterns(self):
        request = self.factory.get("/admin/", {}, format="json")
        user = JWTAuthentication().authenticate(request)
        assert user == None

    def test_backend_raises_user_not_found(self):
        request = self.factory.get("/api/v1/accounts/", {}, format="json")
        access_token = self._generate_access_token(-3)
        request.META["HTTP_AUTHORIZATION"] = "Bearer " + access_token

        with self.assertRaisesRegex(
            exceptions.AuthenticationFailed, "User in given token not found."
        ):
            JWTAuthentication().authenticate(request)

    def test_backend_raises_user_is_deactivated(self):
        request = self.factory.get("/api/v1/accounts/", {}, format="json")
        access_token = self._generate_access_token(self.not_active_user.id)
        request.META["HTTP_AUTHORIZATION"] = "Bearer " + access_token

        with self.assertRaisesRegex(
            exceptions.AuthenticationFailed, "Given user is deactivated."
        ):
            JWTAuthentication().authenticate(request)

    def test_backend_raises_user_is_blocked(self):
        request = self.factory.get("/api/v1/accounts/", {}, format="json")
        access_token = self._generate_access_token(self.blocked_user.id)
        request.META["HTTP_AUTHORIZATION"] = "Bearer " + access_token

        with self.assertRaisesRegex(
            exceptions.AuthenticationFailed, "Given user is blocked."
        ):
            JWTAuthentication().authenticate(request)

    def test_backend_authenticates_valid_user(self):
        request = self.factory.get("/api/v1/accounts/", {}, format="json")
        access_token = self._generate_access_token(self.valid_user.id)
        request.META["HTTP_AUTHORIZATION"] = "Bearer " + access_token
        user, token = JWTAuthentication().authenticate(request)
        assert user == self.valid_user
        assert token == access_token

    def _generate_access_token(self, user_id: int) -> str:
        payload = {
            "user_id": user_id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=0, minutes=30),
            "iat": datetime.datetime.utcnow(),
        }
        priv_key = serialization.load_pem_private_key(
            settings.ACCESS_PRIVATE_KEY,
            settings.ACCESS_PASSPHRASE,
            backend=default_backend(),
        )
        access_token = jwt.encode(payload, priv_key, algorithm="RS256")
        return access_token
