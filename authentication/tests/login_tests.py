import pytest

from rest_framework.test import APIClient

from accounts.models import User


@pytest.fixture
def users():
    User.objects.create_user(
        username="test_user", password="test_password", email="test@gmail.com"
    )
    User.objects.create_user(
        username="blocked_user",
        password="test_password",
        email="blocked@gmail.com",
        is_blocked=True,
    )


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
@pytest.mark.usefixtures("users")
class TestAuthenticationLoginView:
    def test_login_returns_username_and_password_required(self, api_client):
        response = api_client.post("/api/v1/auth/login/", {}, format="json")

        assert response.status_code == 400
        assert response.data == {
            "username": ["This field is required."],
            "password": ["This field is required."],
        }

    def test_login_returns_user_not_found(self, api_client):
        response = api_client.post(
            "/api/v1/auth/login/",
            {"username": "wrong_user", "password": "wrong_password"},
        )
        assert response.status_code == 400
        assert response.data == {"username": ["user with such username not found"]}

    def test_login_returns_user_is_blocked(self, api_client):
        response = api_client.post(
            "/api/v1/auth/login/",
            {"username": "blocked_user", "password": "wrong_password"},
        )
        assert response.status_code == 400
        assert response.data == {"username": ["this user is blocked."]}

    def test_login_returns_wrong_password(self, api_client):
        response = api_client.post(
            "/api/v1/auth/login/",
            {"username": "test_user", "password": "wrong_password"},
        )
        assert response.status_code == 400
        assert response.data == {"password": ["wrong password for this user"]}

    def test_login_authenticates_user(self, api_client):
        response = api_client.post(
            "/api/v1/auth/login/",
            {"username": "test_user", "password": "test_password"},
        )
        assert response.status_code == 200
        assert response.data["access_token"] != None
        assert response.data["expires_in"] != None
        assert response.data["token_type"] == "Bearer"
