from django.test import TestCase

from accounts.models import User

from rest_framework.test import APIClient

class AuthenticationLoginViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test_user", password="test_password", email="test@gmail.com"
        )
        self.client = APIClient()

    def test_login_returns_username_and_password_required(self):
        response = self.client.post("/api/v1/auth/login/", {}, format="json")

        assert response.status_code == 400
        assert response.data == {
            "username": ["This field is required."],
            "password": ["This field is required."],
        }

    def test_login_returns_user_not_found(self):
        response = self.client.post(
            "/api/v1/auth/login/",
            {"username": "wrong_user", "password": "wrong_password"},
        )
        assert response.status_code == 400
        assert response.data == {"username": ["user with such username not found"]}

    def test_login_returns_wrong_password(self):
        response = self.client.post(
            "/api/v1/auth/login/",
            {"username": "test_user", "password": "wrong_password"},
        )
        assert response.status_code == 400
        assert response.data == {"password": ["wrong password for this user"]}

    def test_login_authenticates_user(self):
        response = self.client.post(
            "/api/v1/auth/login/",
            {"username": "test_user", "password": "test_password"},
        )
        assert response.status_code == 200
        assert response.data["access_token"] != None
        assert response.data["expires_in"] != None
        assert response.data["token_type"] == "Bearer"
        # хз как проверить то, что в куки возвращается refresh_token...
