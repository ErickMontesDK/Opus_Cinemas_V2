import pytest
from django.db import IntegrityError

from accounts.models import User


@pytest.mark.django_db
def test_create_user_stores_lowercase_email_and_hashed_password():
    user = User.objects.create_user(email="Ana@Example.COM", password="secret-pass-123")

    assert user.email == "ana@example.com"
    assert user.password != "secret-pass-123"
    assert user.check_password("secret-pass-123")
    assert not user.is_staff
    assert not user.is_superuser
    assert str(user) == "ana@example.com"


@pytest.mark.django_db
def test_create_user_requires_email():
    with pytest.raises(ValueError):
        User.objects.create_user(email="", password="secret-pass-123")


@pytest.mark.django_db
def test_create_superuser_sets_staff_flags():
    admin = User.objects.create_superuser(email="admin@example.com", password="secret-pass-123")

    assert admin.is_staff
    assert admin.is_superuser


@pytest.mark.django_db
def test_email_is_unique_regardless_of_case():
    User.objects.create_user(email="ana@example.com", password="secret-pass-123")

    with pytest.raises(IntegrityError):
        User.objects.create_user(email="ANA@example.com", password="secret-pass-123")


@pytest.mark.django_db
def test_get_by_natural_key_ignores_case(user):
    assert User.objects.get_by_natural_key("ANA@Example.com") == user
