from django.test import TestCase

from accounts.models import User

from rest_framework.test import APIClient

from innotter.settings import ACCESS_PRIVATE, ACCESS_PHRASE

import jwt
import datetime
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization


class RegistrationViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test_user", password="test_password", email="test@gmail.com"
        )
        self.client = APIClient()

    def test_registration_returns_required_fields(self):
        response = self.client.post("/api/v1/accounts/registration/", {})

        assert response.status_code == 400
        assert response.data == {
            "username": ["This field is required."],
            "email": ["This field is required."],
            "first_name": ["This field is required."],
            "last_name": ["This field is required."],
            "password": ["This field is required."],
            "password_again": ["This field is required."],
        }

    def test_registration_creates_user(self):
        data = {
            "username": "test_username",
            "email": "test_email@gmail.com",
            "first_name": "test_name",
            "last_name": "test_surname",
            "password": "test_passoword",
            "password_again": "test_passoword",
        }

        response = self.client.post(
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

    def test_registration_with_with_same_data_returns_already_exists(self):
        data = {
            "username": "test_user",
            "email": "test@gmail.com",
            "first_name": "test_name",
            "last_name": "test_surname",
            "password": "test_passoword",
            "password_again": "test_passoword",
        }
        response = self.client.post("/api/v1/accounts/registration/", data)
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
            "password_again": "test_passoword",
        }
        response = self.client.post("/api/v1/accounts/registration/", data)
        assert response.status_code == 400
        assert response.data == {"password": "Passwords must match."}


class PasswordResetViewTestCase(TestCase):
    def setUp(self):
        User.objects.all().delete()
        self.user = User.objects.create_user(
            username="test_user", password="test_password", email="test@gmail.com"
        )
        self.client = APIClient()
        access_token = self.create_access_token(self.user.id)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token)

    def test_password_reset_returns_required_fields(self):
        response = self.client.patch("/api/v1/accounts/password_reset/", {})

        assert response.status_code == 400
        assert response.data == {
            "password": ["This field is required."],
            "new_password": ["This field is required."],
        }

    def test_password_reset_with_with_same_data_returns_error(self):
        data = {
            "password": "test_password",
            "new_password": "test_password",
        }
        response = self.client.patch("/api/v1/accounts/password_reset/", data)
        assert response.status_code == 400
        assert response.data == {"new_password": "Must differ from old password"}

    def test_password_reset_returns_wrong_password(self):
        data = {
            "password": "test_passwordasdjl;kj",
            "new_password": "test_password1",
        }
        response = self.client.patch("/api/v1/accounts/password_reset/", data)
        assert response.status_code == 400
        assert response.data == {"password": "You enetered wrong password"}

    def test_password_reset_updates_user(self):
        data = {
            "password": "test_password",
            "new_password": "test_password1",
        }

        response = self.client.patch("/api/v1/accounts/password_reset/", data)
        assert response.status_code == 201

    def create_access_token(self, user_id):
        payload = {
            "user_id": user_id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=0, minutes=10),
            "iat": datetime.datetime.utcnow(),
        }
        priv_key = serialization.load_pem_private_key(
            ACCESS_PRIVATE, ACCESS_PHRASE, backend=default_backend()
        )
        access_token = jwt.encode(payload, priv_key, algorithm="RS256")
        return access_token
