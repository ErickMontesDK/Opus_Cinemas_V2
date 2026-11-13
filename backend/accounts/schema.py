from drf_spectacular.extensions import OpenApiAuthenticationExtension

from .cookies import ACCESS_COOKIE


class CookieJWTScheme(OpenApiAuthenticationExtension):
    target_class = "accounts.authentication.CookieJWTAuthentication"
    name = "cookieAuth"
    # Wins over drf-spectacular's built-in simplejwt extension, which describes a Bearer header.
    priority = 1

    def get_security_definition(self, auto_schema):
        return {"type": "apiKey", "in": "cookie", "name": ACCESS_COOKIE}
