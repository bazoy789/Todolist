from typing import Any

import pytest

from rest_framework.test import APIClient

pytest_plugins = "tests.factories"


@pytest.fixture
def client() -> APIClient:
    return APIClient()


@pytest.fixture
def auth_client(client: APIClient, user: Any) -> APIClient:
    client.force_login(user)
    return client


@pytest.fixture
@pytest.mark.django_db
def auth_for_lesson(client: Any, django_user_model: Any) -> dict:
    username = "admin"
    password = "admin"

    django_user_model.objects.create_user(
        username=username, password=password)

    response = client.post(
        "/auth/login/",
        {"username": username, "password": password},
        format='json'
    )

    return response
