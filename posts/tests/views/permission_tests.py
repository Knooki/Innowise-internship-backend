import pytest
import datetime
import jwt

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from rest_framework.test import APIClient
from django.conf import settings as set
from django.db.models import Q

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
    non_follower = User.objects.create_user(
        username="not_follower_user",
        password="test_password",
        email="not_follower@gmail.com",
        role="user",
    )
    User.objects.create_user(
        username="admin_user",
        password="test_password",
        email="admin@gmail.com",
        role="admin",
    )
    User.objects.create_user(
        username="moderator_user",
        password="test_password",
        email="moderator@gmail.com",
        role="moderator",
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
    Page.objects.create(
        name="non_owner_page",
        uuid="3456",
        description="non_owner",
        owner=non_follower,
    )


@pytest.fixture
def owner():
    user = User.objects.get(username="owner_user")
    return user


@pytest.fixture
def owner_api_client():
    api_client = APIClient()
    user = User.objects.get(username="owner_user")
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


@pytest.fixture
def simple_user_api_client():
    api_client = APIClient()
    user = User.objects.get(username="simple_user")
    access_token = "Bearer " + create_access_token(user.id)
    api_client.credentials(HTTP_AUTHORIZATION=access_token)
    return api_client


@pytest.fixture
def not_follower_api_client():
    api_client = APIClient()
    user = User.objects.get(username="not_follower_user")
    access_token = "Bearer " + create_access_token(user.id)
    api_client.credentials(HTTP_AUTHORIZATION=access_token)
    return api_client


@pytest.fixture
def admin_api_client():
    api_client = APIClient()
    user = User.objects.get(username="admin_user")
    access_token = "Bearer " + create_access_token(user.id)
    api_client.credentials(HTTP_AUTHORIZATION=access_token)
    return api_client


@pytest.fixture
def moderator_api_client():
    api_client = APIClient()
    user = User.objects.get(username="moderator_user")
    access_token = "Bearer " + create_access_token(user.id)
    api_client.credentials(HTTP_AUTHORIZATION=access_token)
    return api_client


@pytest.mark.django_db
@pytest.mark.usefixtures("users_and_pages")
class TestPagePermissions:
    @pytest.mark.parametrize(
        "api_client",
        ["moderator_api_client", "admin_api_client", "simple_user_api_client"],
    )
    def test_permission_on_list(self, api_client, request):
        api_client = request.getfixturevalue(api_client)
        response = api_client.get("/api/v1/pages/")
        assert response.data != {
            "detail": "You do not have permission to perform this action."
        }
        assert response.status_code == 200

    @pytest.mark.parametrize(
        "api_client",
        ["moderator_api_client", "admin_api_client", "simple_user_api_client"],
    )
    def test_permission_on_retrieve(self, api_client, request):
        api_client = request.getfixturevalue(api_client)
        page = Page.objects.first()
        response = api_client.get(f"/api/v1/pages/{page.id}/")
        assert response.data != {
            "detail": "You do not have permission to perform this action."
        }
        assert response.status_code == 200

    @pytest.mark.parametrize(
        "api_client",
        ["owner_api_client", "simple_user_api_client"],
    )
    def test_permission_on_create(self, api_client, request):
        api_client = request.getfixturevalue(api_client)
        response = api_client.post("/api/v1/pages/")
        assert response.data != {
            "detail": "You do not have permission to perform this action."
        }
        assert response.status_code == 400

    @pytest.mark.parametrize(
        "api_client",
        ["admin_api_client", "moderator_api_client"],
    )
    def test_permission_on_create_negative(self, api_client, request):
        api_client = request.getfixturevalue(api_client)
        response = api_client.post("/api/v1/pages/")
        assert response.data == {
            "detail": "You do not have permission to perform this action."
        }
        assert response.status_code == 403

    @pytest.mark.parametrize(
        "api_client",
        ["simple_user_api_client"],
    )
    def test_permission_on_follow(self, api_client, request):
        api_client = request.getfixturevalue(api_client)
        page = Page.objects.first()
        response = api_client.patch(f"/api/v1/pages/{page.id}/follow/")
        assert response.data != {
            "detail": "You do not have permission to perform this action."
        }
        assert response.status_code == 200

    @pytest.mark.parametrize(
        "api_client",
        ["admin_api_client", "moderator_api_client"],
    )
    def test_permission_on_follow_negative(self, api_client, request):
        api_client = request.getfixturevalue(api_client)
        page = Page.objects.first()
        response = api_client.patch(f"/api/v1/pages/{page.id}/follow/")
        assert response.data == {
            "detail": "You do not have permission to perform this action."
        }
        assert response.status_code == 403

    @pytest.mark.parametrize(
        "api_client",
        ["owner_api_client"],
    )
    def test_permission_on_partial_update(self, api_client, request):
        api_client = request.getfixturevalue(api_client)
        page = Page.objects.first()
        response = api_client.patch(f"/api/v1/pages/{page.id}/")
        assert response.data != {
            "detail": "You do not have permission to perform this action."
        }
        assert response.status_code == 200

    @pytest.mark.parametrize(
        "api_client",
        ["admin_api_client", "moderator_api_client", "simple_user_api_client"],
    )
    def test_permission_on_partial_update_negative(self, api_client, request):
        api_client = request.getfixturevalue(api_client)
        page = Page.objects.first()
        response = api_client.patch(f"/api/v1/pages/{page.id}/")
        assert response.data == {
            "detail": "You do not have permission to perform this action."
        }
        assert response.status_code == 403

    @pytest.mark.parametrize(
        "api_client",
        ["owner_api_client"],
    )
    def test_permission_on_follow_requests(self, api_client, request, owner):
        api_client = request.getfixturevalue(api_client)
        page = Page.objects.filter(Q(owner=owner.id) & Q(is_private=True)).first()
        response = api_client.patch(f"/api/v1/pages/{page.id}/follow_requests/")
        assert response.status_code == 200

    @pytest.mark.parametrize(
        "api_client",
        [
            "follower_api_client",
            "admin_api_client",
            "owner_api_client",
            "moderator_api_client",
        ],
    )
    def test_permission_on_follow_requests_negative(self, api_client, request, owner):
        api_client = request.getfixturevalue(api_client)
        page = Page.objects.exclude(owner=owner).first()
        response = api_client.patch(f"/api/v1/pages/{page.id}/follow_requests/")
        assert response.data == {
            "detail": "You do not have permission to perform this action."
        }
        assert response.status_code == 403

    @pytest.mark.parametrize(
        "api_client",
        [
            "owner_api_client",
            "admin_api_client",
            "moderator_api_client",
        ],
    )
    def test_permission_on_destroy(self, api_client, request, owner):
        api_client = request.getfixturevalue(api_client)
        page = Page.objects.filter(owner=owner).first()
        response = api_client.delete(f"/api/v1/pages/{page.id}/")
        assert response.data != {
            "detail": "You do not have permission to perform this action."
        }
        assert response.status_code == 204

    @pytest.mark.parametrize(
        "api_client",
        [
            "owner_api_client",
            "follower_api_client",
            "simple_user_api_client",
        ],
    )
    def test_permission_on_destroy_negative(self, api_client, request, owner):
        api_client = request.getfixturevalue(api_client)
        page = Page.objects.exclude(owner=owner).first()
        response = api_client.delete(f"/api/v1/pages/{page.id}/")
        assert response.data == {
            "detail": "You do not have permission to perform this action."
        }
        assert response.status_code == 403

    @pytest.mark.parametrize(
        "api_client",
        [
            "admin_api_client",
            "moderator_api_client",
        ],
    )
    def test_permission_on_blocktime(self, api_client, request):
        api_client = request.getfixturevalue(api_client)
        page = Page.objects.first()
        response = api_client.patch(f"/api/v1/pages/{page.id}/blocktime/")
        assert response.data != {
            "detail": "You do not have permission to perform this action."
        }
        assert response.status_code == 200

    @pytest.mark.parametrize(
        "api_client",
        [
            "owner_api_client",
            "simple_user_api_client",
            "follower_api_client",
        ],
    )
    def test_permission_on_blocktime_negative(self, api_client, request):
        api_client = request.getfixturevalue(api_client)
        page = Page.objects.first()
        response = api_client.patch(f"/api/v1/pages/{page.id}/blocktime/")
        assert response.data == {
            "detail": "You do not have permission to perform this action."
        }
        assert response.status_code == 403

    @pytest.mark.parametrize(
        "api_client",
        [
            "follower_api_client",
        ],
    )
    def test_permission_on_unfollow(self, api_client, request):
        api_client = request.getfixturevalue(api_client)
        page = Page.objects.first()
        response = api_client.patch(f"/api/v1/pages/{page.id}/unfollow/")
        assert response.data != {
            "detail": "You do not have permission to perform this action."
        }
        assert response.status_code == 200

    @pytest.mark.parametrize(
        "api_client",
        [
            "not_follower_api_client",
            "simple_user_api_client",
            "owner_api_client",
            "admin_api_client",
            "moderator_api_client",
        ],
    )
    def test_permission_on_unfollow(self, api_client, request):
        api_client = request.getfixturevalue(api_client)
        page = Page.objects.first()
        response = api_client.patch(f"/api/v1/pages/{page.id}/unfollow/")
        assert response.data == {
            "detail": "You do not have permission to perform this action."
        }
        assert response.status_code == 403
