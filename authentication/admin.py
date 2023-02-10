from django.contrib import admin

from .models import UserToken

class UserTokenAdmin(admin.ModelAdmin):
    model=UserToken
    list_display=(
        "user_id",
        "is_valid",
        "expires_at",
        "created_at",
    )
    
admin.site.register(UserToken, UserTokenAdmin)