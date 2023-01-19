from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


class UserAdmin(UserAdmin):
    
    readonly_fields=[
        "date_joined",
    ]
    model = User
    list_display = [
        "email",
        "username",
        "role",
        "title",
        "first_name",
        "last_name",
        "is_staff",
        "is_blocked",
    ]
    fieldsets = UserAdmin.fieldsets + ((None, {"fields": ("role", "title", "is_blocked",)}),)
    add_fieldsets = UserAdmin.add_fieldsets + ((None, {"fields": ("email", "first_name", "last_name", "role", "title", "is_blocked",)}),)
    
    
admin.site.register(User, UserAdmin)