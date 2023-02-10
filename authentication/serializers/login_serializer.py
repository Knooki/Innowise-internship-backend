from rest_framework import serializers

from accounts.models import User


MSG = {
    "NotFound": {"username": "user with such username not found"},
    "IsBlocked": {"username": "this user is blocked."},
    "WrongPassword": {"password": "wrong password for this user"},
}


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")
        user = User.objects.filter(username=username).first()
        if not user:
            raise serializers.ValidationError(MSG["NotFound"], code="authorization")
        if user.is_blocked:
            raise serializers.ValidationError(MSG["IsBlocked"], code="authorization")
        if not user.check_password(password):
            raise serializers.ValidationError(
                MSG["WrongPassword"], code="authorization"
            )

        return user.id
