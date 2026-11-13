import pytest
from django.urls import reverse

from accounts.cookies import ACCESS_COOKIE

from .test_auth_api import login

ME_URL = reverse("me")


@pytest.mark.django_db
def test_me_returns_401_for_anonymous_user(api_client):
    response = api_client.get(ME_URL)

    assert response.status_code == 401


def test_me_returns_the_logged_in_user(csrf_client, user):
    login(csrf_client)

    response = csrf_client.get(ME_URL)

    assert response.status_code == 200
    assert response.json() == {
        "id": user.id,
        "email": "ana@example.com",
        "first_name": "Ana",
        "last_name": "Lopez",
    }


def test_me_works_without_csrf_header(csrf_client, api_client, user):
    login(csrf_client)
    # A fresh client with only the access cookie: GET is a safe method, so no CSRF header needed.
    api_client.cookies[ACCESS_COOKIE] = csrf_client.cookies[ACCESS_COOKIE].value

    response = api_client.get(ME_URL)

    assert response.status_code == 200


@pytest.mark.django_db
def test_me_returns_401_for_invalid_access_cookie(api_client):
    api_client.cookies[ACCESS_COOKIE] = "not-a-real-token"

    response = api_client.get(ME_URL)

    assert response.status_code == 401


def test_me_returns_401_after_logout(csrf_client, user):
    login(csrf_client)
    csrf_client.post(reverse("auth-logout"))

    response = csrf_client.get(ME_URL)

    assert response.status_code == 401


@pytest.mark.parametrize("method", ["post", "put", "patch", "delete"])
def test_me_is_read_only(csrf_client, user, method):
    login(csrf_client)

    response = getattr(csrf_client, method)(ME_URL)

    assert response.status_code == 405
