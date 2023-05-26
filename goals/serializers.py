from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied

from core.serializers import UserSerializer
from goals.models import GoalCategory, Goal, GoalComments


class GoalCategorySerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalCategory
        fields = "__all__"
        read_only_fields = ("id", "created", "updated", "user", "is_deleted")


class GoalCategoryWithUserSerializer(GoalCategorySerializer):
    user = UserSerializer(read_only=True)


class GoalSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Goal
        fields = "__all__"
        read_only_fields = ("id", "created", "updated", "user")

    def validate_category(self, value: GoalCategory) -> GoalCategory:
        if value.is_deleted:
            raise ValidationError("Category not found")
        if self.context["request"].user.id != value.user_id:
            raise PermissionDenied
        return value

    # Написать проверку чтобы дата дедлайна не была меньше текущей


class GoalWithUserSerializer(GoalSerializer):
    user = UserSerializer(read_only=True)


class GoalCommentsSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalComments
        fields = "__all__"
        read_only_fields = ("id", "created", "updated", "user")

    def validate_goal(self, value: Goal) -> Goal:
        if value.status == Goal.Status.archived:
            raise ValidationError("Goal not found")
        if self.context["request"].user.id != value.user_id:
            raise PermissionDenied
        return value


class GoalCommentWithUserSerializer(GoalCommentsSerializer):
    user = UserSerializer(read_only=True)
    goal = serializers.PrimaryKeyRelatedField(read_only=True)
