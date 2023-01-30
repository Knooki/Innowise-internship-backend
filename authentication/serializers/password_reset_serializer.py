from rest_framework import serializers

from accounts.models import User

from django.contrib.auth.hashers import check_password


class PasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)
    new_password = serializers.CharField(
        style={"input_type": "password"}, write_only=True
    )
    new_password_again = serializers.CharField(
        style={"input_type": "password"}, write_only=True
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

    def validate(self, data):
        password = data["password"]
        new_password = data["new_password"]
        new_password_again = data["new_password_again"]
        if not check_password(password, self.user.password):
            raise serializers.ValidationError(
                {"password": "You enetered wrong password"}
            )
        if new_password != new_password_again:
            raise serializers.ValidationError(
                {"new_password_again": "New passwords must be identical"}
            )
        if password == new_password:
            raise serializers.ValidationError(
                {"new_password": "Must differ from old password"}
            )
        return new_password

    def update(self, validated_data):
        new_password = validated_data
        self.user.set_password(new_password)
        self.user.save()
        return self.user
