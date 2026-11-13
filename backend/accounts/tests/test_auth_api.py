import pytest
from django.urls import reverse

from accounts.cookies import REFRESH_COOKIE_PATH
from accounts.models import User

from .conftest import PASSWORD

REGISTER_DATA = {
    "email": "New.User@Example.com",
    "password": "a-strong-pass-123",
    "first_name": "New",
    "last_name": "User",
}


def assert_auth_cookies_set(response):
    access = response.cookies["access"]
    refresh = response.cookies["refresh"]
    assert access.value and refresh.value
    assert access["httponly"] and refresh["httponly"]
    assert access["samesite"] == refresh["samesite"] == "Lax"
    assert access["path"] == "/"
    assert refresh["path"] == REFRESH_COOKIE_PATH


def assert_auth_cookies_deleted(response):
    assert response.cookies["access"].value == ""
    assert response.cookies["refresh"].value == ""
    assert response.cookies["refresh"]["path"] == REFRESH_COOKIE_PATH


def login(client, email="ana@example.com", password=PASSWORD):
    return client.post(reverse("auth-login"), {"email": email, "password": password})


# --- CSRF ---


@pytest.mark.django_db
def test_csrf_endpoint_sets_csrf_cookie(api_client):
    response = api_client.get(reverse("auth-csrf"))

    assert response.status_code == 204
    assert "csrftoken" in response.cookies


@pytest.mark.django_db
@pytest.mark.parametrize("url_name", ["auth-register", "auth-login", "auth-refresh", "auth-logout"])
def test_auth_endpoints_reject_requests_without_csrf_token(api_client, url_name):
    response = api_client.post(reverse(url_name), REGISTER_DATA)

    assert response.status_code == 403
    assert "CSRF" in response.data["detail"]


# --- Register ---


def test_register_creates_user_and_logs_in(csrf_client):
    response = csrf_client.post(reverse("auth-register"), REGISTER_DATA)

    assert response.status_code == 201
    user = User.objects.get(email="new.user@example.com")
    assert response.data == {
        "id": user.id,
        "email": "new.user@example.com",
        "first_name": "New",
        "last_name": "User",
    }
    assert "password" not in response.data
    assert user.check_password("a-strong-pass-123")
    assert_auth_cookies_set(response)


def test_register_rejects_existing_email_in_any_case(csrf_client, user):
    response = csrf_client.post(
        reverse("auth-register"), {**REGISTER_DATA, "email": "ANA@example.com"}
    )

    assert response.status_code == 400
    assert "email" in response.data
    assert User.objects.count() == 1


def test_register_rejects_weak_password(csrf_client):
    response = csrf_client.post(reverse("auth-register"), {**REGISTER_DATA, "password": "12345678"})

    assert response.status_code == 400
    assert "password" in response.data
    assert not User.objects.exists()


def test_register_requires_names(csrf_client):
    data = {**REGISTER_DATA, "first_name": "", "last_name": ""}
    response = csrf_client.post(reverse("auth-register"), data)

    assert response.status_code == 400
    assert {"first_name", "last_name"} <= response.data.keys()


# --- Login ---


def test_login_sets_cookies_and_returns_user(csrf_client, user):
    response = login(csrf_client)

    assert response.status_code == 200
    assert response.data["email"] == "ana@example.com"
    assert_auth_cookies_set(response)


def test_login_email_is_case_insensitive(csrf_client, user):
    response = login(csrf_client, email="ANA@Example.com")

    assert response.status_code == 200


@pytest.mark.parametrize(
    "email, password",
    [("ana@example.com", "wrong-password"), ("nobody@example.com", PASSWORD)],
)
def test_login_rejects_bad_credentials_with_same_message(csrf_client, user, email, password):
    response = login(csrf_client, email=email, password=password)

    assert response.status_code == 401
    assert response.data["detail"] == "No active account found with the given credentials"
    assert "access" not in response.cookies


def test_login_rejects_inactive_user(csrf_client, user):
    user.is_active = False
    user.save()

    assert login(csrf_client).status_code == 401


# --- Refresh ---


def test_refresh_rotates_tokens(csrf_client, user):
    old_refresh = login(csrf_client).cookies["refresh"].value

    response = csrf_client.post(reverse("auth-refresh"))

    assert response.status_code == 204
    assert_auth_cookies_set(response)
    assert response.cookies["refresh"].value != old_refresh


def test_refresh_rejects_a_token_that_was_already_rotated(csrf_client, user):
    old_refresh = login(csrf_client).cookies["refresh"].value
    csrf_client.post(reverse("auth-refresh"))

    # Someone replays the old token, for example after stealing it.
    csrf_client.cookies["refresh"] = old_refresh
    response = csrf_client.post(reverse("auth-refresh"))

    assert response.status_code == 401
    assert_auth_cookies_deleted(response)


def test_refresh_without_cookie_returns_401(csrf_client):
    response = csrf_client.post(reverse("auth-refresh"))

    assert response.status_code == 401


def test_refresh_rejects_garbage_token(csrf_client):
    csrf_client.cookies["refresh"] = "not-a-token"

    response = csrf_client.post(reverse("auth-refresh"))

    assert response.status_code == 401


# --- Logout ---


def test_logout_deletes_cookies_and_revokes_refresh_token(csrf_client, user):
    refresh = login(csrf_client).cookies["refresh"].value

    response = csrf_client.post(reverse("auth-logout"))

    assert response.status_code == 204
    assert_auth_cookies_deleted(response)

    csrf_client.cookies["refresh"] = refresh
    assert csrf_client.post(reverse("auth-refresh")).status_code == 401


def test_logout_works_without_cookies(csrf_client):
    response = csrf_client.post(reverse("auth-logout"))

    assert response.status_code == 204
