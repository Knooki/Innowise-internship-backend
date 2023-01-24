from rest_framework import serializers

from accounts.serializers import UserSerializer
from .models import Post, Page, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class PageSerializer(serializers.ModelSerializer):
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
            "follow_requests",
            "unblock_date",
        )
        depth = 1


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "page",
            "content",
            "reply_to",
            "created_at",
            "updated_at",
        )
        depth = 1
