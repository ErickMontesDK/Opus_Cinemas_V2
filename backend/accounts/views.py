from django.core.exceptions import ObjectDoesNotExist
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from .authentication import CSRFProtectedMixin
from .cookies import REFRESH_COOKIE, delete_auth_cookies, set_auth_cookies
from .serializers import RegisterSerializer, UserSerializer


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CSRFView(APIView):
    """Set the `csrftoken` cookie that the frontend copies into the X-CSRFToken header."""

    permission_classes = [AllowAny]

    @extend_schema(responses={204: None})
    def get(self, request):
        return Response(status=status.HTTP_204_NO_CONTENT)


class RegisterView(CSRFProtectedMixin, APIView):
    """Create an account and log the new user in."""

    permission_classes = [AllowAny]

    @extend_schema(request=RegisterSerializer, responses={201: UserSerializer})
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        response = Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        set_auth_cookies(response, str(refresh.access_token), str(refresh))
        return response


class LoginView(CSRFProtectedMixin, APIView):
    """Check email and password and set the auth cookies."""

    permission_classes = [AllowAny]

    @extend_schema(request=TokenObtainPairSerializer, responses={200: UserSerializer})
    def post(self, request):
        # simplejwt checks the credentials and builds the tokens; we only move them to cookies.
        serializer = TokenObtainPairSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        tokens = serializer.validated_data

        response = Response(UserSerializer(serializer.user).data)
        set_auth_cookies(response, tokens["access"], tokens["refresh"])
        return response


class RefreshView(CSRFProtectedMixin, APIView):
    """Rotate the tokens using the refresh cookie."""

    permission_classes = [AllowAny]

    @extend_schema(request=None, responses={204: None, 401: None})
    def post(self, request):
        raw_refresh = request.COOKIES.get(REFRESH_COOKIE)
        if raw_refresh is None:
            return self._unauthorized()

        serializer = TokenRefreshSerializer(data={"refresh": raw_refresh})
        try:
            serializer.is_valid(raise_exception=True)
        except (TokenError, AuthenticationFailed, ObjectDoesNotExist):
            # Expired, blacklisted, or the user was deleted or deactivated.
            return self._unauthorized()

        tokens = serializer.validated_data
        response = Response(status=status.HTTP_204_NO_CONTENT)
        set_auth_cookies(response, tokens["access"], tokens["refresh"])
        return response

    def _unauthorized(self):
        response = Response(
            {"detail": "Session expired. Please log in again."},
            status=status.HTTP_401_UNAUTHORIZED,
        )
        delete_auth_cookies(response)
        return response


class LogoutView(CSRFProtectedMixin, APIView):
    """Blacklist the refresh token and delete the auth cookies."""

    permission_classes = [AllowAny]

    @extend_schema(request=None, responses={204: None})
    def post(self, request):
        raw_refresh = request.COOKIES.get(REFRESH_COOKIE)
        if raw_refresh is not None:
            try:
                RefreshToken(raw_refresh).blacklist()
            except TokenError:
                pass  # Already expired or blacklisted: nothing left to revoke.

        response = Response(status=status.HTTP_204_NO_CONTENT)
        delete_auth_cookies(response)
        return response


class MeView(RetrieveAPIView):
    """Return the logged-in user, or 401 so the frontend knows it must refresh or log in."""

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # No id in the URL: the object is always the user who sent the request.
        return self.request.user
