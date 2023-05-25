from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from goals.models import GoalCategory, GoalComments, Goal


# Register your models here.

@admin.register(GoalCategory)
class GoalCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "title")
    readonly_fields = ("created", "updated")
    list_filter = ["is_deleted"]
    search_fields = ["title"]


class CommentsInLine(admin.StackedInline):
    model = GoalComments
    extra = 0


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ("id", "title")
    search_fields = ("title", "description")
    readonly_fields = ("created", "updated")
    list_filter = ("status", "priority")
    inlines = [CommentsInLine]

    def author_link(self, obj: Goal) -> Goal:
        return format_html(
            "<a href='{url}'>{user_name}</a>",
            url=reverse("admin:core_user_change", kwargs={"object_id": obj.user_id}),
            user_name=obj.user.username
        )

    author_link.short_description = "Author"
