from django.contrib import admin

from core.models import User
from django.contrib.auth.models import Group


class AuthorAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "first_name", "last_name")
    list_filter = ("username", "first_name", "last_name")
    search_fields = ("is_staff", "is_active", "is_superuser")
    readonly_fields = ("last_login", "date_joined")
    exclude = ("password",)


admin.site.register(User, AuthorAdmin)
admin.site.unregister(Group)
