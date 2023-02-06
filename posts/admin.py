from django.contrib import admin

from .models import Tag, Page, Post


class TagAdmin(admin.ModelAdmin):
    model = Tag
    list_display = ("name",)


class PageAdmin(admin.ModelAdmin):
    model = Page
    list_display = (
        "uuid",
        "name",
        "description",
        "owner",
        "image",
        "is_private",
    )


class PostAdmin(admin.ModelAdmin):
    readonly_fields = ("created_at",)
    model = Post
    list_display = (
        "title",
        "page",
        "content",
        "reply_to",
    )


admin.site.register(Tag, TagAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(Post, PostAdmin)
