from typing import Any
from unittest.mock import ANY

import pytest
from rest_framework import status
from rest_framework.test import APIClient



@pytest.mark.django_db
class TestCoreLogin:
    url = "/core/login"

    def test_core_login(self, client: APIClient, auth_for_lesson: Any) -> None:

        response = client.post(self.url, data={"username": "admin", "password": "admin"})

        assert response.status_code == status.HTTP_200_OK

    def test_core_false_login(self, client: APIClient, auth_for_lesson: Any) -> None:
        response = client.post(self.url, data={"username": "123", "password": "admin"})

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestCoreProfile:
    url = "/core/profile"

    def test_core_profile(self, auth_client: APIClient) -> None:
        """
        Проверяет что профиль существует
        """
        response = auth_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == self._data_profile()

    def _data_profile(self, **kwargs: Any) -> dict:
        data = {
            "id": ANY,
            "username": ANY,
            "first_name": ANY,
            "last_name": ANY,
            "email": ANY,
        }
        data |= kwargs
        return data

    def test_core_profile_update(self, auth_client: APIClient) -> None:
        """
        Проверяет что пользователь может изменить свой профиль
        """
        response = auth_client.put(self.url, data={"username": "12345"})

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == self._data_profile_update()

    def _data_profile_update(self, **kwargs: Any) -> dict:
        data = {
            "id": ANY,
            "username": "12345",
            "first_name": ANY,
            "last_name": ANY,
            "email": ANY,
        }
        data |= kwargs
        return data

    def test_core_profile_delete(self, auth_client: APIClient) -> None:
        """
        Проверяет что авторизованный пользователь может удалить профиль
        """
        response = auth_client.delete(self.url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_core_profile_delete_not_user(self, client: APIClient) -> None:
        """
        Проверяет что не авторизованный пользователь не может удалить профиль
        """
        response = client.delete(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestCoreSignup:
    url = "/core/signup"

    def test_core_signup(self, client: APIClient) -> None:
        """
        Проверяет регистрацию пользователя
        """
        response = client.post(self.url, data={"username": "admin1",
                                               "password": "qaz1wsx2edc3",
                                               "password_repeat": "qaz1wsx2edc3"})

        assert response.status_code == status.HTTP_201_CREATED
