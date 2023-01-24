import pytest
import jwt
import datetime
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

from .jwt_token_exceptions import (
    AccessTokenExpired,
    AccessTokenNotFound,
    InvalidAccessToken,
    BearerKeywordNotFound,
)

from rest_framework.test import APIClient

from .settings import ACCESS_PHRASE, ACCESS_PRIVATE


@pytest.fixture
def client():
    client = APIClient()
    return client


@pytest.fixture
def valid_access_token_fixture():
    payload = {
        "user_id": 1,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=0, minutes=30),
        "iat": datetime.datetime.utcnow(),
    }
    priv_key = serialization.load_pem_private_key(
        ACCESS_PRIVATE, ACCESS_PHRASE, backend=default_backend()
    )
    access_token = jwt.encode(payload, priv_key, algorithm="RS256")
    return access_token


@pytest.fixture
def expired_access_token_fixture():
    payload = {
        "user_id": 1,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=0, minutes=0),
        "iat": datetime.datetime.utcnow(),
    }
    priv_key = serialization.load_pem_private_key(
        ACCESS_PRIVATE, ACCESS_PHRASE, backend=default_backend()
    )
    access_token = jwt.encode(payload, priv_key, algorithm="RS256")
    return access_token


@pytest.mark.django_db
def test_middleware_skips_unauthenticated_urls(client):
    client.get("/api/v1/auth/refresh", {}, format="json")


@pytest.mark.django_db
def test_middleware_skips_valid_token(valid_access_token_fixture, client):
    client.credentials(HTTP_AUTHORIZATION="Bearer " + valid_access_token_fixture)
    client.get("/api/v1/accounts/", {}, format="json")


def test_middleware_raises_AccessTokenExpired(expired_access_token_fixture, client):
    client.credentials(HTTP_AUTHORIZATION="Bearer " + expired_access_token_fixture)
    with pytest.raises(AccessTokenExpired) as e_info:
        client.get("/api/v1/accounts/", {}, format="json")


def test_middleware_raises_AccessTokenNotFound(client):
    client.credentials()
    with pytest.raises(AccessTokenNotFound) as e_info:
        client.get("/api/v1/accounts/", {}, format="json")


def test_middleware_raises_NoKeywordInAuthorization(client):
    client.credentials(HTTP_AUTHORIZATION="Token")
    with pytest.raises(BearerKeywordNotFound) as e_info:
        client.get("/api/v1/accounts/", {}, format="json")


def test_middleware_raises_InvalidAccessToken(client):
    client.credentials(HTTP_AUTHORIZATION="Bearer " + "Invalid Token")
    with pytest.raises(InvalidAccessToken) as e_info:
        client.get("/api/v1/accounts/", {}, format="json")
    