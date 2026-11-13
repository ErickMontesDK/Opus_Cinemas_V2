from rest_framework.authentication import CSRFCheck
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from rest_framework_simplejwt.authentication import JWTAuthentication

from .cookies import ACCESS_COOKIE


def enforce_csrf(request):
    """Run Django's CSRF check, the same way DRF's SessionAuthentication does."""

    def dummy_get_response(request):
        return None

    check = CSRFCheck(dummy_get_response)
    check.process_request(request)
    reason = check.process_view(request, None, (), {})
    if reason:
        raise PermissionDenied(f"CSRF Failed: {reason}")


class CookieJWTAuthentication(JWTAuthentication):
    """Read the access token from its httpOnly cookie instead of the Authorization header."""

    def authenticate(self, request):
        raw_token = request.COOKIES.get(ACCESS_COOKIE)
        if raw_token is None:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
            user = self.get_user(validated_token)
        except AuthenticationFailed:
            # An expired cookie must not break public endpoints; protected ones still return 401.
            return None

        # The browser sends cookies on its own, so a request using them must prove it came from us.
        enforce_csrf(request)
        return user, validated_token


class CSRFProtectedMixin:
    """Enforce CSRF on views that run before the user is authenticated (login, register...)."""

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        enforce_csrf(request)
