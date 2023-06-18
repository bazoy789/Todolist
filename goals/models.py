from typing import Any

from django.db import models

from core.models import User
from todolist.models import BaseModel


class Board(BaseModel):
    title = models.CharField(verbose_name="Название", max_length=255)
    is_deleted = models.BooleanField(verbose_name="Удалена", default=False)

    def __str__(self) -> Any:
        return self.title

    class Meta:
        verbose_name = "Доска"
        verbose_name_plural = "Доски"


class BoardParticipant(BaseModel):
    class Meta:
        unique_together = ("board", "user")
        verbose_name = "Участник"
        verbose_name_plural = "Участники"

    class Role(models.IntegerChoices):
        owner = 1, "Владелец"
        writer = 2, "Редактор"
        reader = 3, "Читатель"

    board = models.ForeignKey(Board, verbose_name="Доска", on_delete=models.PROTECT, related_name="participants")
    user = models.ForeignKey(User, verbose_name="Пользователь", on_delete=models.PROTECT, related_name="participants")
    role = models.PositiveSmallIntegerField(verbose_name="Роль", choices=Role.choices, default=Role.owner)

    editable_roles: list[tuple[int, str]] = Role.choices[1:]


class GoalCategory(BaseModel):
    title = models.CharField(verbose_name="Название", max_length=255)
    user = models.ForeignKey(User, verbose_name="Автор", on_delete=models.PROTECT)
    is_deleted = models.BooleanField(verbose_name="Удалена", default=False)
    board = models.ForeignKey(Board, on_delete=models.PROTECT, related_name="categories")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self) -> Any:
        return self.title


class Goal(BaseModel):
    class Status(models.IntegerChoices):
        to_do = 1, "К выполнению"
        in_progress = 2, "В процессе"
        done = 3, "Выполнено"
        archived = 4, "Архив"

    class Priority(models.IntegerChoices):
        low = 1, "Низкий"
        medium = 2, "Средний"
        high = 3, "Высокий"
        critical = 4, "Критический"

    title = models.CharField(verbose_name="Название", max_length=255)
    descriptions = models.TextField(blank=True)
    category = models.ForeignKey(GoalCategory, on_delete=models.PROTECT)
    due_date = models.DateField(null=True, blank=True)
    user = models.ForeignKey(User, verbose_name="Автор", on_delete=models.PROTECT)
    status = models.PositiveSmallIntegerField(verbose_name="Статус",
                                              choices=Status.choices,
                                              default=Status.to_do)
    priority = models.PositiveSmallIntegerField(verbose_name="Приоритет",
                                                choices=Priority.choices,
                                                default=Priority.medium)

    def __str__(self) -> Any:
        return self.title

    class Meta:
        verbose_name = "Цель"
        verbose_name_plural = "Цели"


class GoalComments(BaseModel):
    user = models.ForeignKey(User, verbose_name="Автор", on_delete=models.PROTECT)
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE)
    text = models.TextField()

    def __str__(self) -> Any:
        return self.text
