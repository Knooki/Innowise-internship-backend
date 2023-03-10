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
def users_and_pages():
    owner_user = User.objects.create_user(
        username="owner_user",
        password="test_password",
        email="owner@gmail.com",
        role="user",
    )
    User.objects.create_user(
        username="admin_user",
        password="test_password",
        email="admin@gmail.com",
        role="admin",
    )
    Page.objects.create(
        name="page",
        uuid="1234",
        description="page",
        owner=owner_user,
    )


@pytest.fixture
def admin_api_client():
    api_client = APIClient()
    user = User.objects.get(username="admin_user")
    access_token = "Bearer " + create_access_token(user.id)
    api_client.credentials(HTTP_AUTHORIZATION=access_token)
    return api_client


@pytest.mark.django_db
@pytest.mark.usefixtures("users_and_pages")
class TestPageBlocktimeAction:
    def test_blocktime_action_blocks_permanently(self, admin_api_client, request):
        page = Page.objects.get(name="page")
        response = admin_api_client.patch(
            f"/api/v1/pages/{page.id}/blocktime/", {"is_permanent_blocked": True}
        )
        page = Page.objects.get(name="page")
        assert page.is_permanent_blocked == True
        assert response.status_code == 200

    def test_blocktime_action_blocks_temporarily(self, admin_api_client, request):
        page = Page.objects.get(name="page")
        response = admin_api_client.patch(
            f"/api/v1/pages/{page.id}/blocktime/", {"blocktime_in_minutes": 2}
        )
        page = Page.objects.get(name="page")
        assert page.is_permanent_blocked == False
        assert pytz.UTC.localize(datetime.datetime.now()) < page.unblock_date
        assert response.status_code == 200

    def test_blocktime_action_unblocks(self, admin_api_client, request):
        page = Page.objects.get(name="page")
        response = admin_api_client.patch(f"/api/v1/pages/{page.id}/blocktime/")
        page = Page.objects.get(name="page")
        assert page.is_permanent_blocked == False
        assert page.unblock_date == None
        assert response.status_code == 200
