import pytest
import jwt
import datetime

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from django.conf import settings as set
from rest_framework import exceptions
from rest_framework.test import APIRequestFactory

from accounts.models import User
from authentication.backends import JWTAuthentication


def generate_access_token(user_id: int) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=0, minutes=30),
        "iat": datetime.datetime.utcnow(),
    }
    priv_key = serialization.load_pem_private_key(
        set.ACCESS_PRIVATE_KEY,
        set.ACCESS_PASSPHRASE,
        backend=default_backend(),
    )
    access_token = jwt.encode(payload, priv_key, algorithm="RS256")
    return access_token


@pytest.fixture
def not_active_user_token():
    user = User.objects.create_user(
        username="not_active_user",
        password="test_password",
        email="not.active@gmail.com",
        is_active=False,
    )
    return generate_access_token(user.id)


@pytest.fixture
def blocked_user_token():
    user = User.objects.create_user(
        username="blocked_user",
        password="test_password",
        email="blocked@gmail.com",
        is_blocked=True,
    )
    return generate_access_token(user.id)


@pytest.fixture
def valid_user_token():
    user = User.objects.create_user(
        username="test_user", password="test_password", email="test@gmail.com"
    )
    return generate_access_token(user.id)


@pytest.fixture
def invalid_user_token():
    return generate_access_token(-3)


@pytest.fixture
def api_factory():
    return APIRequestFactory()


@pytest.mark.django_db
class TestAuthenticationBackend:
    def test_backend_returns_null_if_unauthenticated_url_patterns(self, api_factory):
        request = api_factory.get("/admin/", {}, format="json")
        user = JWTAuthentication().authenticate(request)
        assert user == None

    def test_backend_raises_user_not_found(self, api_factory, invalid_user_token):
        request = api_factory.get("/api/v1/accounts/", {}, format="json")
        access_token = invalid_user_token
        request.META["HTTP_AUTHORIZATION"] = "Bearer " + access_token

        with pytest.raises(
            exceptions.AuthenticationFailed, match="User in given token not found."
        ):
            JWTAuthentication().authenticate(request)

    @pytest.mark.usefixtures("not_active_user_token")
    def test_backend_raises_user_is_deactivated(
        self, api_factory, not_active_user_token
    ):
        request = api_factory.get("/api/v1/accounts/", {}, format="json")
        access_token = not_active_user_token
        request.META["HTTP_AUTHORIZATION"] = "Bearer " + access_token

        with pytest.raises(
            exceptions.AuthenticationFailed, match="Given user is deactivated."
        ):
            JWTAuthentication().authenticate(request)

    @pytest.mark.usefixtures("blocked_user_token")
    def test_backend_raises_user_is_blocked(self, api_factory, blocked_user_token):
        request = api_factory.get("/api/v1/accounts/", {}, format="json")
        access_token = blocked_user_token
        request.META["HTTP_AUTHORIZATION"] = "Bearer " + access_token

        with pytest.raises(
            exceptions.AuthenticationFailed, match="Given user is blocked."
        ):
            JWTAuthentication().authenticate(request)

    @pytest.mark.usefixtures("valid_user_token")
    def test_backend_authenticates_valid_user(self, api_factory, valid_user_token):
        request = api_factory.get("/api/v1/accounts/", {}, format="json")
        access_token = valid_user_token
        request.META["HTTP_AUTHORIZATION"] = "Bearer " + access_token
        user, token = JWTAuthentication().authenticate(request)
        assert User.objects.filter(id=user.id)
        assert token == access_token
