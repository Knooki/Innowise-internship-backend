from rest_framework import serializers

from accounts.models import User

from django.conf import settings


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")
        user = User.objects.filter(username=username).first()
        if not user:
            msg = {"username": "user with such username not found"}
            raise serializers.ValidationError(msg, code="authorization")
        if not user.check_password(password):
            msg = {"password": "wrong password for this user"}
            raise serializers.ValidationError(msg, code="authorization")

        return user.id
