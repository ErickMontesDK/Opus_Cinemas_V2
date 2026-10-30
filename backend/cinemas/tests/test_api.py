from datetime import datetime, time, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

import pytest
from django.urls import reverse
from django.utils import timezone

from cinemas.models import Auditorium, Showtime
from movies.models import Movie

VANCOUVER = ZoneInfo("America/Vancouver")


@pytest.fixture
def movie(db):
    return Movie.objects.create(tmdb_id=1, title="Dune", runtime=120)


@pytest.fixture
def other_movie(db):
    return Movie.objects.create(tmdb_id=2, title="Arrival", runtime=116)


@pytest.fixture
def auditorium(db):
    return Auditorium.objects.create(name="Auditorium 1", rows=2, columns=2)


def create_showtime(movie, auditorium, starts_at):
    # objects.create() skips clean(), so overlaps do not matter in these tests.
    return Showtime.objects.create(
        movie=movie, auditorium=auditorium, starts_at=starts_at, base_price=Decimal("12.50")
    )


def get_showtimes(client, **params):
    return client.get(reverse("showtime-list"), params)


def test_showtime_list_returns_expected_fields(client, movie, auditorium):
    showtime = create_showtime(movie, auditorium, timezone.now() + timedelta(days=1))

    response = get_showtimes(client)

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": showtime.id,
            "movie": movie.id,
            "auditorium": "Auditorium 1",
            "starts_at": timezone.localtime(showtime.starts_at).isoformat(),
            "ends_at": timezone.localtime(showtime.ends_at).isoformat(),
            "base_price": "12.50",
        }
    ]


def test_showtime_list_excludes_past_showtimes(client, movie, auditorium):
    create_showtime(movie, auditorium, timezone.now() - timedelta(hours=1))
    upcoming = create_showtime(movie, auditorium, timezone.now() + timedelta(hours=1))

    response = get_showtimes(client)

    assert [s["id"] for s in response.json()] == [upcoming.id]


def test_showtime_list_filters_by_movie(client, movie, other_movie, auditorium):
    tomorrow = timezone.now() + timedelta(days=1)
    dune = create_showtime(movie, auditorium, tomorrow)
    create_showtime(other_movie, auditorium, tomorrow + timedelta(hours=3))

    response = get_showtimes(client, movie=movie.id)

    assert [s["id"] for s in response.json()] == [dune.id]


@pytest.mark.django_db
def test_showtime_list_rejects_invalid_movie(client):
    response = get_showtimes(client, movie="abc")

    assert response.status_code == 400
    assert "movie" in response.json()


def test_showtime_list_filters_by_local_date(client, movie, auditorium):
    day = timezone.localdate() + timedelta(days=1)

    late_night = create_showtime(
        movie, auditorium, datetime.combine(day, time(23, 30), tzinfo=VANCOUVER)
    )
    create_showtime(
        movie, auditorium, datetime.combine(day + timedelta(days=1), time(18, 0), tzinfo=VANCOUVER)
    )

    response = get_showtimes(client, date=day.isoformat())

    assert [s["id"] for s in response.json()] == [late_night.id]


@pytest.mark.parametrize("value", ["2026-13-45", "hola"])
@pytest.mark.django_db
def test_showtime_list_rejects_invalid_date(client, value):
    response = get_showtimes(client, date=value)

    assert response.status_code == 400
    assert "date" in response.json()
