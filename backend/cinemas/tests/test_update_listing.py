from datetime import date, datetime, time, timedelta
from io import StringIO
from unittest import mock

import pytest
from django.core.management import CommandError, call_command
from django.utils import timezone

from cinemas.management.commands.update_listing import (
    EVENING_PRICE,
    LAST_START,
    MATINEE_PRICE,
    plan_day,
    price_for,
    round_up,
)
from cinemas.models import Auditorium, Seat, Showtime
from movies.models import Movie
from movies.tmdb import TMDBClientError

# TMDB is replaced in every test: the command is tested without network access.
COMMAND = "cinemas.management.commands.update_listing"
RUNTIMES = {1: 100, 2: 120, 3: 95, 4: None, 5: 140}


def fake_import_movie(tmdb_id):
    """Stand-in for `import_movie` that saves a local movie instead of calling TMDB."""
    return Movie.objects.update_or_create(
        tmdb_id=tmdb_id,
        defaults={"title": f"Movie {tmdb_id}", "runtime": RUNTIMES.get(tmdb_id, 110)},
    )


def run(now_playing=(1, 2, 3), import_side_effect=fake_import_movie, **options):
    out, err = StringIO(), StringIO()
    with (
        mock.patch(f"{COMMAND}.fetch_now_playing", return_value=list(now_playing)),
        mock.patch(f"{COMMAND}.import_movie", side_effect=import_side_effect),
    ):
        call_command("update_listing", stdout=out, stderr=err, **options)
    return out.getvalue(), err.getvalue()


def local(day, hour, minute=0):
    return timezone.make_aware(datetime.combine(day, time(hour, minute)))


# --- Pure helpers (no database) ---


@pytest.mark.parametrize(
    ("minute", "expected"),
    [(0, 0), (1, 15), (14, 15), (15, 15), (46, 0)],
)
def test_round_up_moves_to_the_next_quarter_hour(minute, expected):
    rounded = round_up(local(date(2026, 11, 10), 14, minute))

    assert rounded.minute == expected


def test_price_depends_on_local_start_time():
    day = date(2026, 11, 10)

    assert price_for(local(day, 16, 59)) == MATINEE_PRICE
    assert price_for(local(day, 17, 0)) == EVENING_PRICE


def test_plan_day_chains_shows_and_rotates_movies():
    day = date(2026, 11, 10)
    # 100 min + 15 cleaning = 115 -> next show at 13:55, rounded up to 14:00.
    a = Movie(title="A", runtime=100)
    b = Movie(title="B", runtime=120)

    slots = plan_day(day, [a, b], offset=1)

    assert slots[0] == (b, local(day, 12, 0))
    # 120 + 15 = 135 min -> 14:15.
    assert slots[1] == (a, local(day, 14, 15))
    assert slots[2] == (b, local(day, 16, 15))
    assert all(timezone.localtime(s).time() <= LAST_START for _, s in slots)


# --- The command ---


@pytest.mark.django_db
def test_creates_auditoriums_with_seats_and_wheelchair_spaces():
    run()

    assert list(Auditorium.objects.values_list("name", "rows", "columns")) == [
        ("Auditorium 1", 10, 14),
        ("Auditorium 2", 8, 12),
        ("Auditorium 3", 6, 10),
    ]
    auditorium = Auditorium.objects.get(name="Auditorium 1")
    assert auditorium.seats.count() == 140
    wheelchair = auditorium.seats.filter(seat_type=Seat.SeatType.WHEELCHAIR)
    assert sorted(s.label for s in wheelchair) == ["A1", "A14"]


@pytest.mark.django_db
def test_schedules_every_auditorium_every_day_without_overlaps():
    run(days=3)

    today = timezone.localdate()
    for auditorium in Auditorium.objects.all():
        for offset in range(3):
            shows = list(
                auditorium.showtimes.filter(starts_at__date=today + timedelta(days=offset))
            )
            assert shows, f"{auditorium} has no showtimes on day {offset}"
            # Ordered by starts_at: each show must end before the next one starts.
            for previous, following in zip(shows, shows[1:], strict=False):
                assert previous.ends_at <= following.starts_at

    assert not Showtime.objects.filter(starts_at__date=today + timedelta(days=3)).exists()


@pytest.mark.django_db
def test_running_twice_creates_nothing_new():
    run(days=2)
    counts = (Auditorium.objects.count(), Seat.objects.count(), Showtime.objects.count())

    out, _ = run(days=2)

    assert (Auditorium.objects.count(), Seat.objects.count(), Showtime.objects.count()) == counts
    assert "Scheduled 0 showtimes; skipped 6 auditorium days" in out


@pytest.mark.django_db
def test_a_later_run_only_fills_the_new_days():
    run(days=1)
    first_day = set(Showtime.objects.values_list("id", flat=True))

    run(now_playing=(5,), days=2)

    # Day one keeps its showtimes; day two uses the new listing.
    assert first_day <= set(Showtime.objects.values_list("id", flat=True))
    tomorrow = timezone.localdate() + timedelta(days=1)
    new_movies = Showtime.objects.filter(starts_at__date=tomorrow).values_list(
        "movie__tmdb_id", flat=True
    )
    assert set(new_movies) == {5}


@pytest.mark.django_db
def test_skips_failed_and_runtime_less_movies_and_takes_the_next_ones():
    def import_or_fail(tmdb_id):
        if tmdb_id == 2:
            raise TMDBClientError("404 Not Found")
        return fake_import_movie(tmdb_id)

    out, err = run(now_playing=(1, 2, 4, 3, 5), import_side_effect=import_or_fail, movies=3)

    assert "Skipped 2: 404 Not Found" in err
    assert "Skipped Movie 4: no runtime on TMDB" in err
    scheduled = set(Showtime.objects.values_list("movie__tmdb_id", flat=True))
    assert scheduled == {1, 3, 5}


@pytest.mark.django_db
def test_fails_when_no_movie_can_be_imported():
    with pytest.raises(CommandError, match="No movies could be imported"):
        run(import_side_effect=TMDBClientError("TMDB_API_TOKEN is not set"))

    # Nothing is created when the movies step fails.
    assert not Auditorium.objects.exists()


@pytest.mark.django_db
def test_fails_when_now_playing_cannot_be_fetched():
    with mock.patch(f"{COMMAND}.fetch_now_playing", side_effect=TMDBClientError("timed out")):
        with pytest.raises(CommandError, match="Could not fetch the movies now playing"):
            call_command("update_listing", stdout=StringIO())
