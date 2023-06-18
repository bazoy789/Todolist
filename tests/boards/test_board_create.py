from typing import Callable, Any
from unittest.mock import ANY

import pytest
from faker import Faker
from rest_framework import status

from rest_framework.test import APIClient
from goals.models import Board, BoardParticipant


@pytest.fixture
def board_create_data(faker: Faker) -> Callable:
    def _wrapper(**kwargs: Any) -> dict:
        data = {"title": faker.sentence(2)}
        data |= kwargs
        return data
    return _wrapper


@pytest.mark.django_db
class TestBoardCreate:
    url = "/goals/board/create"

    def test_auth(self, client: APIClient, board_create_data: Any) -> None:
        """
        Проверяет авторизован ли пользователь если нет поучаем ошибку
        """
        response = client.post(self.url, data=board_create_data())
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_failed_to_create_deleted_board(self, auth_client: APIClient, board_create_data: Any) -> None:
        """
        Нельзя создать удаленную доску
        """
        response = auth_client.post(self.url, data=board_create_data(is_deleted=False))

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == self._serializer_board_response(is_deleted=False)
        assert Board.objects.last().is_deleted is False

    def test_request_user_became_board_owner(self, auth_client: APIClient, user: Any, board_create_data: Any) -> None:
        """
        Проверяет что пользователь может создать доску
        """
        response = auth_client.post(self.url, data=board_create_data())

        assert response.status_code == status.HTTP_201_CREATED
        board_participant = BoardParticipant.objects.get(user_id=user.id)
        assert board_participant.board_id == response.data["id"]
        assert board_participant.role == BoardParticipant.Role.owner

    def _serializer_board_response(self, **kwargs: Any) -> dict:
        data = {
            "id": ANY,
            "created": ANY,
            "updated": ANY,
            "title": ANY,
            "is_deleted": True
        }
        data |= kwargs
        return data
