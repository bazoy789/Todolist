from typing import Any

import pytest
from rest_framework import status

from rest_framework.test import APIClient
from goals.models import BoardParticipant


@pytest.mark.django_db
class TestBoardRetrieve:

    @pytest.fixture(autouse=True)
    def setup(self, board_participant: Any) -> None:
         self.url = self.get_url(board_participant.board_id)

    @staticmethod
    def get_url(board_pk: int) -> str:
        return f"/goals/board/{board_pk}"

    def test_auth(self, client: APIClient) -> None:
        """
        Проверяет авторизован ли пользователь если нет поучаем ошибку
        """
        response = client.get(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_retrieve_deleted_board(self, auth_client: APIClient, board: Any) -> None:
        """
        Проверяет можно ли посмотреть удаленную доску
        """
        board.is_deleted = True
        board.save()
        response = auth_client.get(self.url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_retrieve_foreign_board(self, client: APIClient, user_factory: Any) -> None:
        """
        Проверяет можно ли получить доступ к не своей доске
        """

        another_user = user_factory.create()
        client.force_login(another_user)

        response = client.get(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestBoardDestroy:

    @pytest.fixture(autouse=True)
    def setup(self, board_participant: Any) -> None:
         self.url = self.get_url(board_participant.board_id)

    @staticmethod
    def get_url(board_pk: int) -> str:
        return f"/goals/board/{board_pk}"

    def test_auth(self, client: APIClient) -> None:
        """
        Проверяет авторизован ли пользователь если нет поучаем ошибку
        """
        response = client.delete(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize("role", [
        BoardParticipant.Role.writer,
        BoardParticipant.Role.reader,
    ], ids=["writer", "reader"])
    def test_not_owner_deleted_board(self, client: APIClient, user_factory: Any, board: Any, board_participant_factory: Any, role: str) -> None:
        """
        Проверяет, может ли не владелец доски удалить её
        """
        another_user = user_factory.create()
        board_participant_factory.create(user=another_user, board=board, role=role)
        client.force_login(another_user)

        response = client.delete(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_owner_deleted_board(self, auth_client: APIClient,  board: Any) -> None:
        """
        Проверяет, может ли владелец удалить доску
        """

        response = auth_client.delete(self.url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        board.refresh_from_db()
        assert board.is_deleted is True
