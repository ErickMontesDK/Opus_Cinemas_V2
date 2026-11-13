from datetime import timedelta

import pytest
from django.urls import reverse
from rest_framework.exceptions import PermissionDenied
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory
from rest_framework_simplejwt.tokens import AccessToken

from accounts.authentication import CookieJWTAuthentication


def build_request(method="get", access=None, csrf_token=None):
    factory = APIRequestFactory(enforce_csrf_checks=True)
    if access is not None:
        factory.cookies["access"] = access
    headers = {}
    if csrf_token is not None:
        factory.cookies["csrftoken"] = csrf_token
        headers["HTTP_X_CSRFTOKEN"] = csrf_token
    return Request(getattr(factory, method)("/", **headers))


def expired_token(user):
    token = AccessToken.for_user(user)
    token.set_exp(lifetime=-timedelta(minutes=1))
    return str(token)


@pytest.mark.django_db
def test_valid_cookie_authenticates_user(user):
    token = AccessToken.for_user(user)

    result = CookieJWTAuthentication().authenticate(build_request(access=str(token)))

    assert result is not None
    assert result[0] == user


def test_no_cookie_means_anonymous():
    assert CookieJWTAuthentication().authenticate(build_request()) is None


@pytest.mark.django_db
def test_invalid_or_expired_cookie_means_anonymous(user):
    auth = CookieJWTAuthentication()

    assert auth.authenticate(build_request(access="garbage")) is None
    assert auth.authenticate(build_request(access=expired_token(user))) is None


@pytest.mark.django_db
def test_cookie_on_unsafe_method_requires_csrf_token(user):
    token = str(AccessToken.for_user(user))
    auth = CookieJWTAuthentication()

    with pytest.raises(PermissionDenied):
        auth.authenticate(build_request("post", access=token))

    csrf = "a" * 32
    result = auth.authenticate(build_request("post", access=token, csrf_token=csrf))
    assert result[0] == user


@pytest.mark.django_db
def test_public_endpoint_still_works_with_expired_cookie(api_client, user):
    api_client.cookies["access"] = expired_token(user)

    response = api_client.get(reverse("movie-list"))

    assert response.status_code == 200
