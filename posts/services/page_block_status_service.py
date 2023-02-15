import datetime
import pytz

from django.db.models import Q, Count

from posts.models import Page

utc = pytz.UTC


class PageBlockStatusService:
    def __init__(self, request) -> None:
        self.request = request

    def update_blockstatus_on_all_pages(self):
        queryset = Page.objects.all().filter(
            ~Q(unblock_date=None), is_permanent_blocked=False
        )
        for page in queryset:
            if utc.localize(datetime.datetime.now()) > page.unblock_date:
                page.unblock_date = None
                page.save()

    def get_query_set(self):
        """
        Returns different queryset based on user role.
        """
        user = self.request.user
        queryset = (
            Page.objects.select_related("owner")
            .prefetch_related("tags", "followers", "follow_requests")
            .annotate(followers_count=Count("followers"))
        )
        if user and user.role not in ("admin", "moderator"):
            queryset = queryset.filter(
                is_permanent_blocked=False, unblock_date=None
            ).annotate(followers_count=Count("followers"))

        return queryset
