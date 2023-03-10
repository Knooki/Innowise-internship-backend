import pytest
import datetime
import jwt
import pytz

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
def owner_user() -> User:
    owner_user = User.objects.create_user(
        username="owner_user",
        password="test_password",
        email="owner@gmail.com",
        role="user",
    )
    return owner_user


@pytest.fixture
def simple_user() -> User:
    simple_user = User.objects.create_user(
        username="simple_user",
        password="test_password",
        email="simple@gmail.com",
        role="user",
    )
    return simple_user


@pytest.fixture
def public_page(owner_user, simple_user):
    Page.objects.create(
        name="public_page",
        uuid="1234",
        description="page",
        owner=owner_user,
    ).followers.add(simple_user)

@pytest.fixture
def user_api_client():
    api_client = APIClient()
    user = User.objects.get(username="simple_user")
    access_token = "Bearer " + create_access_token(user.id)
    api_client.credentials(HTTP_AUTHORIZATION=access_token)
    return api_client


@pytest.mark.django_db
class TestPageFollowRequestsAction:
    @pytest.mark.usefixtures("owner_user", "simple_user", "public_page")
    def test_follow_to_public_page(self, user_api_client, simple_user, request):
        page = Page.objects.first()
        response = user_api_client.patch(f"/api/v1/pages/{page.id}/unfollow/")
        page = Page.objects.first()
        assert response.status_code == 200
        assert page.followers.count() == 0
        assert simple_user.id not in page.followers.values_list(flat=True)
