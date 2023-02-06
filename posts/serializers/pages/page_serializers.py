from rest_framework import serializers

from posts.models import Page
from accounts.serializers.user_serializer import UserSerializer


class AdminAccessPageSerializer(serializers.ModelSerializer):

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
        extra_kwargs = {
            "id": {"read_only": True},
            "owner": {"read_only": True},
        }
        depth = 1


class ShortInfoPageSerializer(serializers.ModelSerializer):

    owner = UserSerializer()

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

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["follower_count"] = instance.followers.count()

        return representation


class FullAccessPageSerilizer(serializers.ModelSerializer):

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


class PartialAccessPageSerializer(serializers.ModelSerializer):

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

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["follower_count"] = instance.followers.count()

        return representation
