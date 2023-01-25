from rest_framework import serializers

from .models import User

from django.contrib.auth.hashers import check_password


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "image_s3_path",
            "first_name",
            "last_name",
            "role",
            "title",
            "is_blocked",
        )


class UserRegistrationSerializer(serializers.ModelSerializer):

    password_again = serializers.CharField(
        style={"input_type": "password"}, write_only=True
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "password_again",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
            "password_again": {"write_only": True},
            "first_name": {"required": True},
            "last_name": {"required": True},
        }

    def save(self):
        user = User(
            email=self.validated_data["email"],
            username=self.validated_data["username"],
            first_name=self.validated_data["first_name"],
            last_name=self.validated_data["last_name"],
            role="user",
            is_blocked=False,
        )

        password = self.validated_data["password"]
        password_again = self.validated_data["password_again"]

        if password != password_again:
            raise serializers.ValidationError({"password": "Passwords must match."})
        user.set_password(password)
        user.save()
        return user


class PasswordResetUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)
    new_password = serializers.CharField(
        style={"input_type": "password"}, write_only=True
    )

    class Meta:
        model = User
        fields = [
            "password",
            "new_password",
        ]
        extra_kwargs = {
            "password": {"write_only": True, "required": True},
            "new_password": {"write_only": True, "required": True},
        }

    def __init__(self, user, *args, **kwargs):

        super(PasswordResetUserSerializer, self).__init__(*args, **kwargs)
        self.user = user

    # def validate_password(self, value):

    #     return value

    def update(self, instance, validated_data):
        user = instance
        password = validated_data["password"]
        new_password = validated_data["new_password"]
        if password == new_password:
            raise serializers.ValidationError(
                {"new_password": "Must differ from old password"}
            )
        if not check_password(password, user.password):
            raise serializers.ValidationError(
                {"password": "You enetered wrong password"}
            )

        user.set_password(new_password)
        user.save()
        return user
