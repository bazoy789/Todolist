from django.db import transaction
from rest_framework import generics, permissions, filters, pagination

from goals.models import GoalCategory, Goal
from goals.permissions import GoalCategoryPermission
from goals.serializers import GoalCategorySerializer, GoalCategoryWithUserSerializer


class GoalCategoryCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCategorySerializer


class GoalCategoryListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCategoryWithUserSerializer
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ["title", "created"]
    ordering = ["title"]
    search_fields = ["title"]
    pagination_class = pagination.LimitOffsetPagination

    def get_queryset(self):
        return GoalCategory.objects.select_related("user").filter(user=self.request.user).exclude(is_deleted=True)


class GoalCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [GoalCategoryPermission, ]
    serializer_class = GoalCategoryWithUserSerializer

    def get_queryset(self):
        return GoalCategory.objects.select_related("user").exclude(is_deleted=True)

    def perform_destroy(self, instance: GoalCategory):
        with transaction.atomic():
            instance.is_deleted = True
            instance.save(update_fields=["is_deleted"])
            instance.goal_set.update(status=Goal.Status.archived)
