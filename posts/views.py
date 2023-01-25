from rest_framework import viewsets

from .models import Tag, Post, Page

from .serializers import TagSerializer, PageSerializer, PostSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = ()


class PageViewSet(viewsets.ModelViewSet):
    queryset = Page.objects.select_related("owner").prefetch_related(
        "tags", "followers", "follow_requests"
    )
    serializer_class = PageSerializer
    permission_classes = ()


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.select_related("page", "reply_to")
    serializer_class = PostSerializer
    permission_classes = ()
