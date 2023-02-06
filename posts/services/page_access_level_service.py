from posts.serializers.pages.page_serializers import (
    AdminAccessPageSerializer,
    FullAccessPageSerilizer,
    PartialAccessPageSerializer,
)


class PageAccessLevelService:
    def get_serializer(page, user):
        """
        Depending on private status of the page
        and user identity
        returns proper serializer 
        with restricted/full access to the page info 
        """
        if page.is_private and user not in page.followers.all() and user != page.owner:
            serializer = PartialAccessPageSerializer(page)
        elif user.role in ("admin", "moderator"):
            serializer = AdminAccessPageSerializer(page)
        else:
            serializer = FullAccessPageSerilizer(page)
        return serializer
