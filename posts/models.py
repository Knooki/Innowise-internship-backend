from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self) -> str:
        return self.name


class Page(models.Model):
    name = models.CharField(max_length=80)
    uuid = models.CharField(max_length=30, unique=True)
    description = models.TextField()
    tags = models.ManyToManyField("posts.Tag", related_name="pages")

    owner = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, related_name="pages"
    )
    followers = models.ManyToManyField(
        "accounts.User", related_name="follows", blank=True
    )

    image = models.URLField(null=True, blank=True)

    is_private = models.BooleanField(default=False)
    follow_requests = models.ManyToManyField(
        "accounts.User", related_name="requests", blank=True
    )

    unblock_date = models.DateTimeField(null=True, blank=True)
    is_permanent_blocked = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=30, unique=True)
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="posts")
    content = models.CharField(max_length=180)

    reply_to = models.ForeignKey(
        "posts.Post",
        on_delete=models.SET_NULL,
        null=True,
        related_name="replies",
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title
