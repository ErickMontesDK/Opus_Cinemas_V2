from django.conf import settings
from rest_framework_simplejwt.settings import api_settings

ACCESS_COOKIE = "access"
REFRESH_COOKIE = "refresh"
# The refresh token is only sent to the auth endpoints, not with every request.
REFRESH_COOKIE_PATH = "/api/auth/"
SAMESITE = "Lax"


def set_auth_cookies(response, access, refresh):
    common = {"httponly": True, "secure": settings.AUTH_COOKIE_SECURE, "samesite": SAMESITE}
    response.set_cookie(
        ACCESS_COOKIE,
        access,
        max_age=int(api_settings.ACCESS_TOKEN_LIFETIME.total_seconds()),
        path="/",
        **common,
    )
    response.set_cookie(
        REFRESH_COOKIE,
        refresh,
        max_age=int(api_settings.REFRESH_TOKEN_LIFETIME.total_seconds()),
        path=REFRESH_COOKIE_PATH,
        **common,
    )


def delete_auth_cookies(response):
    # The browser only deletes a cookie when the path matches the one it was set with.
    response.delete_cookie(ACCESS_COOKIE, path="/", samesite=SAMESITE)
    response.delete_cookie(REFRESH_COOKIE, path=REFRESH_COOKIE_PATH, samesite=SAMESITE)
