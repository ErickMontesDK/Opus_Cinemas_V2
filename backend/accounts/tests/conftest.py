import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from accounts.models import User

PASSWORD = "a-strong-pass-123"


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="ana@example.com", password=PASSWORD, first_name="Ana", last_name="Lopez"
    )


@pytest.fixture
def api_client():
    # The test client skips CSRF checks by default; we want them on, like a real browser.
    return APIClient(enforce_csrf_checks=True)


@pytest.fixture
def csrf_client(api_client, db):
    """A client that already has the csrftoken cookie and sends it in the X-CSRFToken header."""
    api_client.get(reverse("auth-csrf"))
    api_client.credentials(HTTP_X_CSRFTOKEN=api_client.cookies["csrftoken"].value)
    return api_client
