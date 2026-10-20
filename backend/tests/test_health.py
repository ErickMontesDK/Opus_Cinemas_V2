from unittest import mock

import pytest
from django.db import OperationalError
from django.urls import reverse


@pytest.mark.django_db
def test_health_returns_ok(client):
    response = client.get(reverse("health"))

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.django_db
def test_health_returns_503_when_database_is_down(client):
    with mock.patch("config.views.connection.cursor", side_effect=OperationalError):
        response = client.get(reverse("health"))

    assert response.status_code == 503
    assert response.json() == {"status": "error"}
