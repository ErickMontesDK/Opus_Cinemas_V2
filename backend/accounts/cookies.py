from django.conf import settings
from rest_framework_simplejwt.settings import api_settings

ACCESS_COOKIE = "access"
REFRESH_COOKIE = "refresh"
# Both cookies use "/" so the Next.js proxy sees the refresh token on page requests (docs/AUTH.md).
COOKIE_PATH = "/"
SAMESITE = "Lax"


def set_auth_cookies(response, access, refresh):
    common = {
        "httponly": True,
        "secure": settings.AUTH_COOKIE_SECURE,
        "samesite": SAMESITE,
        "path": COOKIE_PATH,
    }
    response.set_cookie(
        ACCESS_COOKIE,
        access,
        max_age=int(api_settings.ACCESS_TOKEN_LIFETIME.total_seconds()),
        **common,
    )
    response.set_cookie(
        REFRESH_COOKIE,
        refresh,
        max_age=int(api_settings.REFRESH_TOKEN_LIFETIME.total_seconds()),
        **common,
    )


def delete_auth_cookies(response):
    # The browser only deletes a cookie when the path matches the one it was set with.
    response.delete_cookie(ACCESS_COOKIE, path=COOKIE_PATH, samesite=SAMESITE)
    response.delete_cookie(REFRESH_COOKIE, path=COOKIE_PATH, samesite=SAMESITE)
