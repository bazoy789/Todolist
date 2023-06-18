from typing import Any
from unittest.mock import ANY

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from goals.models import BoardParticipant


@pytest.mark.django_db
class TestGoalCategory:
    url = "/goals/goal_category/create"

    def test_auth(self, client: APIClient) -> None:
        """
        Проверяет авторизован ли пользователь если нет поучаем ошибку
        """
        response = client.post(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_goal_category_create(self, auth_client: APIClient, board_participant_factory: Any, user: Any) -> None:
        """
        Проверяет что авторизованный пользователь может создать категорию и правильно передаются поля
        """
        board_participant = board_participant_factory.create(role=BoardParticipant.Role.owner, user=user)

        response = auth_client.post(self.url, data={"title": "1234", "board": board_participant.board.id})

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == self._data_goal_category()

    def _data_goal_category(self, **kwargs: Any) -> dict:
        data = {
            "id": ANY,
            "created": ANY,
            "updated": ANY,
            "title": "1234",
            "is_deleted": False,
            "board": ANY
        }
        data |= kwargs
        return data


@pytest.mark.django_db
class TestGoalCategoryList:
    url = "/goals/goal_category/list"

    def test_goal_category_list(self, auth_client: APIClient) -> None:
        """
        Проверяет что авторизованный пользователь получает данные по своим категориям
        """
        response = auth_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK

    def test_goal_category_list_not_owner(self, client: APIClient) -> None:
        """
        Проверяет что не авторизованный пользователь не может получить данные по категориям
        """
        response = client.get(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestGoalCategoryRetrieve:

    @pytest.fixture(autouse=True)
    def setup(self, board_participant_factory: Any, goal_category_factory: Any, user: Any) -> None:
        self.url = f"/goals/goal_category/{self._set_data(board_participant_factory, goal_category_factory, user)}"

    @staticmethod
    def _set_data(board_participant_factory: Any, goal_category_factory: Any, user: Any) -> int:
        board_participant = board_participant_factory.create(role=BoardParticipant.Role.owner, user=user)
        goal_category = goal_category_factory.create(board=board_participant.board, user=user)
        return goal_category.id

    def test_auth_not_owner(self, client: APIClient) -> None:
        """
        Проверяет что не авторизованный пользователь не может просматривать категории
        """
        response = client.get(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_auth(self, auth_client: APIClient) -> None:
        """
        Проверяет что авторизованный пользователь может просмотреть свои категории
        """
        response = auth_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK

    def test_deleted_owner_category(self, auth_client: APIClient) -> None:
        """
        Проверяет что авторизованный пользователь может удалить категорию
        """
        response = auth_client.delete(self.url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_deleted_not_owner_category(self, client: APIClient) -> None:
        """
        Проверяет что не авторизованный пользователь не может удалить категорию
        """
        response = client.delete(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
