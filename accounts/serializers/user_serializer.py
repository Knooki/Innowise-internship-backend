from rest_framework import serializers

from accounts.models import User


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
