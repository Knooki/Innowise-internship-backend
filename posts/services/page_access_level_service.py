from posts.serializers.pages.page_serializers import (
    FullAccessPageSerializer,
    FollowerAccessPageSerializer,
    NonFollowerAccessPageSerializer,
)


class PageAccessLevelService:
    def get_serializer(self, page, user):
        """
        Depending on private status of the page
        and user identity
        returns proper serializer
        with restricted/full access to the page info
        """
        if user and (user.role in ("admin", "moderator") or user == page.owner):
            serializer = FullAccessPageSerializer(page)
        elif (
            page.is_private and user not in page.followers.all() and user != page.owner
        ):
            serializer = NonFollowerAccessPageSerializer(page)
        else:
            serializer = FollowerAccessPageSerializer(page)
        return serializer
