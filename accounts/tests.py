from django.test import TestCase

from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import exceptions

from accounts.serializers import UserSerializer
from .views import UserViewSet


class RegistrationViewTestCase(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="test_user", password="test_password", email="test@gmail.com"
        )
        self.client = APIClient()

    def test_registration_returns_required_fields(self):
        response = self.client.post("/api/v1/accounts/registration/", {}, format="json")

        assert response.status_code == 400
        assert response.data == {
            "username": ["This field is required."],
            "email": ["This field is required."],
            "first_name": ["This field is required."],
            "last_name": ["This field is required."],
            "password": ["This field is required."],
            "password2": ["This field is required."],
        }

    def test_registration_creates_user(self):
        data = {
            "username": "test_username",
            "email": "test_email@gmail.com",
            "first_name": "test_name",
            "last_name": "test_surname",
            "password": "test_passoword",
            "password2": "test_passoword",
        }

        response = self.client.post(
            "/api/v1/accounts/registration/",
            data,
        )
        assert response.status_code == 201
        assert response.data == {
            "username": "test_username",
            "email": "test_email@gmail.com",
            "first_name": "test_name",
            "last_name": "test_surname",
        }

    def test_registration_with_with_same_data_returns_already_exists(self):
        data = {
            "username": "test_user",
            "email": "test@gmail.com",
            "first_name": "test_name",
            "last_name": "test_surname",
            "password": "test_passoword",
            "password2": "test_passoword",
        }
        response = self.client.post(
            "/api/v1/accounts/registration/",
            data,
        )
        assert response.status_code == 400
        assert response.data == {
            "username": ["A user with that username already exists."],
            "email": ["user with this email already exists."],
        }

    def test_registration_returns_passwords_must_match(self):
        data = {
            "username": "test_username",
            "email": "test_email@gmail.com",
            "first_name": "test_name",
            "last_name": "test_surname",
            "password": "test_passoword1",
            "password2": "test_passoword",
        }
        response = self.client.post(
            "/api/v1/accounts/registration/",
            data,
        )
        assert response.status_code == 400
        assert response.data == {"password": "Passwords must match."}
