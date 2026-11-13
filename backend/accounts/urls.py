from django.urls import path

from .views import CSRFView, LoginView, LogoutView, RefreshView, RegisterView

urlpatterns = [
    path("csrf/", CSRFView.as_view(), name="auth-csrf"),
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("login/", LoginView.as_view(), name="auth-login"),
    path("refresh/", RefreshView.as_view(), name="auth-refresh"),
    path("logout/", LogoutView.as_view(), name="auth-logout"),
]
