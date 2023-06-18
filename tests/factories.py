from typing import Any

import factory
from django.utils import timezone
from pytest_factoryboy import register

from core.models import User
from goals.models import Board, BoardParticipant, GoalCategory, Goal


@register
class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Faker("user_name")
    password = factory.Faker("password")

    class Meta:
        model = User

    @classmethod
    def _create(cls, model_class: Any, *args: Any, **kwargs: Any) -> User:
        return User.objects.create_user(*args, **kwargs)


class DatasFactoryMixin(factory.django.DjangoModelFactory):
    created = factory.LazyFunction(timezone.now)
    updated = factory.LazyFunction(timezone.now)

    class Meta:
        abstract = True


@register
class BoardFactory(DatasFactoryMixin):
    title = factory.Faker("sentence")

    class Meta:
        model = Board

    @factory.post_generation
    def with_owner(self, model_class: Any, owner: str, **kwargs: Any) -> Any:
        if owner:
            BoardParticipant.objects.create(board=self, user=owner, role=BoardParticipant.Role.owner)


@register
class BoardParticipantFactory(DatasFactoryMixin):
    board = factory.SubFactory(BoardFactory)
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = BoardParticipant


@register
class GoalCategoryFactory(factory.django.DjangoModelFactory):
    title = factory.Faker("sentence")
    board = factory.SubFactory(BoardFactory)

    class Meta:
        model = GoalCategory


@register
class GoalFactory(factory.django.DjangoModelFactory):
    title = factory.Faker("sentence")
    category = factory.SubFactory(GoalCategoryFactory)

    class Meta:
        model = Goal
