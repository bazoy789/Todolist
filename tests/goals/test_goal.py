from typing import Callable, Any

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from goals.models import BoardParticipant, Goal


@pytest.mark.django_db
class TestGoalCreate:
    url = "/goals/goal/create"

    @staticmethod
    def _set_data(board_participant_factory: Any, goal_category_factory: Any, user: Any) -> int:
        board_participant = board_participant_factory.create(role=BoardParticipant.Role.owner, user=user)
        goal_category = goal_category_factory.create(board=board_participant.board, user=user)
        return goal_category.id

    def test_goal_create(self, auth_client: APIClient, board_participant_factory: Any, goal_category_factory: Any, user: Any) -> None:
        """
        Проверяет что авторизованный пользователь может создать Цель
        """
        response = auth_client.post(self.url, data={
            "title": "12345",
            "category": self._set_data(board_participant_factory, goal_category_factory, user)})

        assert response.status_code == status.HTTP_201_CREATED

    def test_goal_create_not_auth(self, client: APIClient, board_participant_factory: Any, goal_category_factory: Any, user: Any) -> None:
        """
        Проверяет что не авторизованный пользователь не может создать Цель
        """
        response = client.post(self.url, data={
            "title": "12345",
            "category": self._set_data(board_participant_factory, goal_category_factory, user)})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_goal_create_to_delete_category(self, auth_client: APIClient, board_participant_factory: Any, goal_category_factory: Any, user: Any) -> None:
        """
        Проверяет что если категория удалена то создать Цель нельзя
        """
        board_participant = board_participant_factory.create(role=BoardParticipant.Role.owner, user=user)
        goal_category = goal_category_factory.create(board=board_participant.board, user=user, is_deleted=True)

        response = auth_client.post(self.url, data={
            "title": "12345",
            "category": goal_category.id})

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestGoalRetrieve:

    @pytest.fixture(autouse=True)
    def setup(self, board_participant_factory: Any, goal_category_factory: Any, user: Any, goal_factory: Any) -> None:
        self.url = f"/goals/goal/{self._set_data(board_participant_factory, goal_category_factory, user, goal_factory).id}"

    @staticmethod
    def _set_data(board_participant_factory: Any, goal_category_factory: Any, user: Any, goal_factory: Any) -> Goal:
        board_participant = board_participant_factory.create(role=BoardParticipant.Role.owner, user=user)
        goal_category = goal_category_factory.create(board=board_participant.board, user=user)
        goal = goal_factory.create(category=goal_category, user=user)
        return goal

    def test_auth_not_owner(self, client: APIClient) -> None:
        """
        Проверяет авторизован ли пользователь если нет поучаем ошибку
        """
        response = client.get(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_auth(self, auth_client: APIClient) -> None:
        """
        Проверяет авторизован ли пользователь
        """
        response = auth_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK

    def test_deleted_owner_category(self, auth_client: APIClient) -> None:
        """
        Проверяет авторизованный пользователь удалить категорию
        """
        response = auth_client.delete(self.url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_deleted_not_owner_category(self, client: APIClient) -> None:
        """
        Проверяет что не владелец категории не может удалить её
        """
        response = client.delete(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

