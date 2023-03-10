from rest_framework import serializers

from posts.models import Page
from accounts.models import User
from accounts.serializers.user_serializer import UserSerializer


class FullAccessPageSerializer(serializers.ModelSerializer):

    owner = UserSerializer()
    followers = UserSerializer(many=True)
    follow_requests = UserSerializer(many=True)

    class Meta:
        model = Page
        fields = (
            "id",
            "name",
            "uuid",
            "description",
            "tags",
            "owner",
            "followers",
            "follow_requests",
            "image",
            "is_private",
            "unblock_date",
            "is_permanent_blocked",
        )
        read_only_fields = (
            "id",
            "owner",
            "unblock_date",
            "is_permanent_blocked",
        )
        depth = 1
    

class NonFollowerAccessPageSerializer(serializers.ModelSerializer):

    owner = UserSerializer()

    class Meta:
        model = Page
        fields = (
            "id",
            "name",
            "uuid",
            "description",
            "tags",
            "owner",
            "image",
            "is_private",
        )
        depth = 1


class FollowerAccessPageSerializer(serializers.ModelSerializer):

    owner = UserSerializer()
    followers = UserSerializer(many=True)

    class Meta:
        model = Page
        fields = (
            "id",
            "name",
            "uuid",
            "description",
            "tags",
            "owner",
            "followers",
            "image",
            "is_private",
        )
        depth = 1


class ShortInfoPageSerializer(serializers.ModelSerializer):

    owner = UserSerializer(required=False)

    class Meta:
        model = Page
        fields = (
            "id",
            "name",
            "uuid",
            "tags",
            "owner",
            "image",
            "is_private",
        )
        extra_kwargs = {
            "id": {"read_only": True},
            "owner": {"read_only": True},
        }
        depth = 1
