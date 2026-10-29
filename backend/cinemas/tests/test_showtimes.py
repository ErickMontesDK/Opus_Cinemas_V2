from datetime import datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from cinemas.models import CLEANING_MINUTES, Auditorium, Showtime
from movies.models import Movie

VANCOUVER = ZoneInfo("America/Vancouver")
# 18:00 + 120 min runtime + 15 min cleaning = 20:15.
SIX_PM = datetime(2026, 11, 1, 18, 0, tzinfo=VANCOUVER)


@pytest.fixture
def movie(db):
    return Movie.objects.create(tmdb_id=1, title="Dune", runtime=120)


@pytest.fixture
def auditorium(db):
    return Auditorium.objects.create(name="Auditorium 1", rows=2, columns=2)


@pytest.fixture
def showtime(movie, auditorium):
    return Showtime.objects.create(
        movie=movie, auditorium=auditorium, starts_at=SIX_PM, base_price=Decimal("12.50")
    )


def build_showtime(movie, auditorium, starts_at):
    # Unsaved showtime, so each test decides whether to validate or save it.
    return Showtime(
        movie=movie, auditorium=auditorium, starts_at=starts_at, base_price=Decimal("12.50")
    )


def test_ends_at_includes_runtime_and_cleaning(showtime):
    assert showtime.ends_at == SIX_PM + timedelta(minutes=120 + CLEANING_MINUTES)


def test_str_shows_vancouver_time(showtime):
    assert str(showtime) == "Dune · Auditorium 1 · 2026-11-01 18:00"


@pytest.mark.parametrize(
    "offset_minutes",
    [
        -60,  # Starts before and ends during the existing showtime
        0,  # Same start time
        60,  # Starts during the existing showtime
    ],
)
def test_overlapping_showtime_in_same_auditorium_is_rejected(showtime, offset_minutes):
    new = build_showtime(
        showtime.movie, showtime.auditorium, SIX_PM + timedelta(minutes=offset_minutes)
    )

    with pytest.raises(ValidationError) as excinfo:
        new.full_clean()

    assert "starts_at" in excinfo.value.error_dict


def test_showtime_can_start_when_previous_one_ends(showtime):
    new = build_showtime(showtime.movie, showtime.auditorium, showtime.ends_at)

    new.full_clean()  # Does not raise


def test_showtime_can_end_when_next_one_starts(showtime):
    # 15:45 + 135 min = 18:00, exactly when the existing showtime starts.
    new = build_showtime(showtime.movie, showtime.auditorium, SIX_PM - timedelta(minutes=135))

    new.full_clean()  # Does not raise


def test_editing_showtime_does_not_overlap_itself(showtime):
    showtime.base_price = Decimal("15.00")

    showtime.full_clean()  # Does not raise


def test_movie_without_runtime_is_rejected(auditorium):
    movie = Movie.objects.create(tmdb_id=2, title="No runtime", runtime=None)
    new = build_showtime(movie, auditorium, SIX_PM)

    with pytest.raises(ValidationError) as excinfo:
        new.full_clean()

    assert "movie" in excinfo.value.error_dict


def test_negative_price_rejected_by_database(movie, auditorium):
    with pytest.raises(IntegrityError), transaction.atomic():
        Showtime.objects.create(
            movie=movie, auditorium=auditorium, starts_at=SIX_PM, base_price=Decimal("-1.00")
        )


def test_same_time_in_another_auditorium_is_allowed(showtime):
    other_auditorium = Auditorium.objects.create(name="Auditorium 2", rows=2, columns=2)
    new = build_showtime(showtime.movie, other_auditorium, SIX_PM)
    new.full_clean()  # Does not raise
