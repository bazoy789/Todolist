from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, filters, permissions, pagination

from goals.models import GoalComments
from goals.permissions import GoalCommentPermission
from goals.serializers import GoalCommentsSerializer, GoalCommentWithUserSerializer


class GoalCommentCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCommentsSerializer


class GoalCommentListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCommentWithUserSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["goal"]
    ordering = ["-created"]
    pagination_class = pagination.LimitOffsetPagination

    def get_queryset(self):
        return GoalComments.objects.filter(goal__category__board__participants__user=self.request.user)


class GoalCommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [GoalCommentPermission]
    serializer_class = GoalCommentWithUserSerializer

    def get_queryset(self):
        return GoalComments.objects.select_related("user").filter(
            goal__category__board__participants__user=self.request.user)
