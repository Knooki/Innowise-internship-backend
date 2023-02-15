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
def simple_user1() -> User:
    simple_user1 = User.objects.create_user(
        username="simple_user1",
        password="test_password",
        email="simple1@gmail.com",
        role="user",
    )
    return simple_user1


@pytest.fixture
def pages(owner_user, simple_user, simple_user1):
    Page.objects.create(
        name="page", uuid="1234", description="page", owner=owner_user, is_private=True
    ).follow_requests.add(simple_user, simple_user1)


@pytest.fixture
def owner_api_client():
    api_client = APIClient()
    user = User.objects.get(username="owner_user")
    access_token = "Bearer " + create_access_token(user.id)
    api_client.credentials(HTTP_AUTHORIZATION=access_token)
    return api_client


@pytest.mark.django_db
class TestPageFollowRequestsAction:
    @pytest.mark.usefixtures("owner_user", "simple_user", "simple_user1", "pages")
    def test_confirm_specific_request(self, owner_api_client, request):
        page = Page.objects.get(uuid="1234")
        follow_request = page.follow_requests.first()
        response = owner_api_client.patch(
            f"/api/v1/pages/{page.id}/follow_requests/{follow_request.id}/"
        )
        assert page.follow_requests.count() == 1
        assert page.followers.count() == 1
        assert follow_request.id in page.followers.values_list(flat=True)
        assert follow_request.id not in page.follow_requests.values_list(flat=True)
        assert response.status_code == 200

    @pytest.mark.usefixtures("owner_user", "simple_user", "simple_user1", "pages")
    def test_confirm_all_requests(self, owner_api_client, request):
        page = Page.objects.get(uuid="1234")
        response = owner_api_client.patch(f"/api/v1/pages/{page.id}/follow_requests/")
        assert page.follow_requests.count() == 0
        assert page.followers.count() == 2
        assert response.status_code == 200

    @pytest.mark.usefixtures("owner_user", "simple_user", "simple_user1", "pages")
    def test_deny_all_requests(self, owner_api_client, request):
        page = Page.objects.get(uuid="1234")
        response = owner_api_client.patch(
            f"/api/v1/pages/{page.id}/follow_requests/?is_confirmed=False"
        )
        assert page.follow_requests.count() == 0
        assert page.followers.count() == 0
        assert response.status_code == 200

    @pytest.mark.usefixtures("owner_user", "simple_user", "simple_user1", "pages")
    def test_deny_specific_request(self, owner_api_client, request):
        page = Page.objects.get(uuid="1234")
        follow_request = page.follow_requests.first()
        response = owner_api_client.patch(
            f"/api/v1/pages/{page.id}/follow_requests/{follow_request.id}/?is_confirmed=False"
        )
        assert page.follow_requests.count() == 1
        assert page.followers.count() == 0
        assert follow_request.id not in page.followers.values_list(flat=True)
        assert follow_request.id not in page.follow_requests.values_list(flat=True)
        assert response.status_code == 200
