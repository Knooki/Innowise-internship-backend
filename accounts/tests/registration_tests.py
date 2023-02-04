import pytest

from rest_framework.test import APIClient

from accounts.models import User


@pytest.fixture
def user():
    user = User.objects.create_user(
        username="test_user", password="test_password", email="test@gmail.com"
    )
    return user


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def valid_user():
    return {
        "username": "test_username",
        "email": "test_email@gmail.com",
        "first_name": "test_name",
        "last_name": "test_surname",
        "password": "test_passoword",
        "confirm_password": "test_passoword",
    }


@pytest.fixture
def same_user():
    return {
        "username": "test_user",
        "email": "test@gmail.com",
        "first_name": "test_name",
        "last_name": "test_surname",
        "password": "test_passoword",
        "confirm_password": "test_passoword",
    }


@pytest.fixture
def diff_pass():
    return {
        "username": "test_username",
        "email": "test_email@gmail.com",
        "first_name": "test_name",
        "last_name": "test_surname",
        "password": "test_passoword1",
        "confirm_password": "test_passoword",
    }


@pytest.mark.django_db
class TestRegistrationView:
    def test_registration_returns_required_fields(self, api_client):
        response = api_client.post("/api/v1/accounts/registration/", {})

        assert response.status_code == 400
        assert response.data == {
            "username": ["This field is required."],
            "email": ["This field is required."],
            "first_name": ["This field is required."],
            "last_name": ["This field is required."],
            "password": ["This field is required."],
            "confirm_password": ["This field is required."],
        }

    def test_registration_creates_user(self, api_client, valid_user):
        data = valid_user

        response = api_client.post(
            "/api/v1/accounts/registration/",
            data,
        )
        assert User.objects.filter(username="test_username").exists() == True
        assert response.status_code == 201
        assert response.data == {
            "username": "test_username",
            "email": "test_email@gmail.com",
            "first_name": "test_name",
            "last_name": "test_surname",
        }

    @pytest.mark.usefixtures("user")
    def test_registration_returns_already_exists(self, api_client, same_user):
        data = same_user
        response = api_client.post("/api/v1/accounts/registration/", data)
        assert response.status_code == 400
        assert response.data == {
            "username": ["A user with that username already exists."],
            "email": ["user with this email already exists."],
        }

    def test_registration_returns_passwords_must_match(self, api_client, diff_pass):
        data = diff_pass
        response = api_client.post("/api/v1/accounts/registration/", data)
        assert response.status_code == 400
        assert response.data == {"password": "Passwords must match."}
