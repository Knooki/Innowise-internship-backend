import pytest
import datetime
import jwt

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from rest_framework.test import APIClient
from django.conf import settings as set

from accounts.models import User
from posts.models import Page


def create_access_token(user_id):
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
    refresh_token = jwt.encode(payload, priv_key, algorithm="RS256")
    return refresh_token


@pytest.fixture
def users_and_pages():
    owner_user = User.objects.create_user(
        username="owner_user",
        password="test_password",
        email="owner@gmail.com",
        role="user",
    )
    follower_user = User.objects.create_user(
        username="follower_user",
        password="test_password",
        email="follower@gmail.com",
        role="user",
    )
    User.objects.create_user(
        username="simple_user",
        password="test_password",
        email="simple@gmail.com",
        role="user",
    )
    User.objects.create_user(
        username="admin_user",
        password="test_password",
        email="admin@gmail.com",
        role="admin",
    )
    Page.objects.create(
        name="public_page",
        uuid="1234",
        description="public",
        owner=owner_user,
    ).followers.add(follower_user)
    Page.objects.create(
        name="private_page",
        uuid="2345",
        description="private",
        owner=owner_user,
        is_private=True,
    ).followers.add(follower_user)


@pytest.fixture
def owner_api_client():
    api_client = APIClient()
    user = User.objects.get(username="owner_user")
    access_token = "Bearer " + create_access_token(user.id)
    api_client.credentials(HTTP_AUTHORIZATION=access_token)
    return api_client


@pytest.fixture
def simple_user_api_client():
    api_client = APIClient()
    user = User.objects.get(username="simple_user")
    access_token = "Bearer " + create_access_token(user.id)
    api_client.credentials(HTTP_AUTHORIZATION=access_token)
    return api_client


@pytest.fixture
def admin_moderator_api_client():
    api_client = APIClient()
    user = User.objects.get(username="admin_user")
    access_token = "Bearer " + create_access_token(user.id)
    api_client.credentials(HTTP_AUTHORIZATION=access_token)
    return api_client

@pytest.fixture
def follower_api_client():
    api_client = APIClient()
    user = User.objects.get(username="follower_user")
    access_token = "Bearer " + create_access_token(user.id)
    api_client.credentials(HTTP_AUTHORIZATION=access_token)
    return api_client


@pytest.mark.django_db
@pytest.mark.usefixtures("users_and_pages")
class TestPageRetrieveAction:
    def test_retrieve_action_with_owner_access(self, owner_api_client, request):
        page = Page.objects.get(name="private_page")
        response = owner_api_client.get(f"/api/v1/pages/{page.id}/")
        assert "followers" in response.data
        assert "description" in response.data
        assert "unblock_date" in response.data
        assert "is_permanent_blocked" in response.data
        assert response.status_code == 200

    def test_retrieve_with_partial_access(self, simple_user_api_client, request):
        page = Page.objects.get(name="private_page")
        response = simple_user_api_client.get(f"/api/v1/pages/{page.id}/")
        assert "followers" not in response.data
        assert "description" in response.data
        assert "unblock_date" not in response.data
        assert "is_permanent_blocked" not in response.data
        assert response.status_code == 200

    def test_retrieve_with_admin_access(self, admin_moderator_api_client, request):
        page = Page.objects.first()
        response = admin_moderator_api_client.get(f"/api/v1/pages/{page.id}/")
        assert "followers" in response.data
        assert "unblock_date" in response.data
        assert "is_permanent_blocked" in response.data
        assert response.status_code == 200
        
    def test_retrieve_with_follower_access(self, follower_api_client, request):
        page = Page.objects.first()
        response = follower_api_client.get(f"/api/v1/pages/{page.id}/")
        assert "followers" in response.data
        assert "description" in response.data
        assert "unblock_date" not in response.data
        assert "is_permanent_blocked" not in response.data
        assert response.status_code == 200