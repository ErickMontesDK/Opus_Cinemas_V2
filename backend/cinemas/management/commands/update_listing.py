"""Seed or refresh the demo listing: auditoriums, movies now in theaters and showtimes.

The first run fills an empty database; later runs only schedule the days that
have no showtimes yet, so it is safe to run again at any time.
"""

from datetime import datetime, time, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from cinemas.models import CLEANING_MINUTES, Auditorium, Seat, Showtime
from movies.importer import import_movie
from movies.tmdb import TMDBClientError, fetch_now_playing

# (name, rows, columns)
AUDITORIUMS = [
    ("Auditorium 1", 10, 14),
    ("Auditorium 2", 8, 12),
    ("Auditorium 3", 6, 10),
]
FIRST_SHOW = time(12, 0)
LAST_START = time(22, 0)
SLOT_MINUTES = 15
EVENING_STARTS = time(17, 0)
MATINEE_PRICE = Decimal("14.00")
EVENING_PRICE = Decimal("17.50")


def round_up(dt):
    """Move a datetime forward to the next multiple of SLOT_MINUTES."""
    # Start times are built from whole minutes, so seconds are always 0.
    remainder = dt.minute % SLOT_MINUTES
    if remainder:
        dt += timedelta(minutes=SLOT_MINUTES - remainder)
    return dt


def price_for(starts_at):
    if timezone.localtime(starts_at).time() >= EVENING_STARTS:
        return EVENING_PRICE
    return MATINEE_PRICE


def plan_day(day, movies, offset):
    """Return `(movie, starts_at)` pairs for one auditorium on one local day.

    Movies rotate in order starting at `offset`; each show starts when the
    previous one ends (runtime + cleaning), rounded up to the next slot.
    """
    starts_at = timezone.make_aware(datetime.combine(day, FIRST_SHOW))
    last_start = timezone.make_aware(datetime.combine(day, LAST_START))

    slots = []
    index = offset
    while starts_at <= last_start:
        movie = movies[index % len(movies)]
        slots.append((movie, starts_at))
        # Same formula as Showtime.ends_at, so consecutive shows never overlap.
        ends_at = starts_at + timedelta(minutes=movie.runtime + CLEANING_MINUTES)
        starts_at = round_up(ends_at)
        index += 1
    return slots


class Command(BaseCommand):
    help = "Create auditoriums, import the movies now in theaters and schedule showtimes."

    def add_arguments(self, parser):
        parser.add_argument("--movies", type=int, default=6, help="How many movies to show")
        parser.add_argument("--days", type=int, default=7, help="Days to schedule from today")

    def handle(self, *args, **options):
        # HTTP calls happen before the transaction, so it is never held open by the network.
        movies = self.import_movies(options["movies"])

        with transaction.atomic():
            auditoriums = self.create_auditoriums()
            created, skipped = self.schedule(auditoriums, movies, options["days"])

        self.stdout.write(
            self.style.SUCCESS(
                f"Scheduled {created} showtimes; skipped {skipped} auditorium days "
                "that already had showtimes."
            )
        )

    def import_movies(self, count):
        try:
            tmdb_ids = fetch_now_playing()
        except TMDBClientError as e:
            raise CommandError(f"Could not fetch the movies now playing: {e}") from e

        movies = []
        # Walk the whole list so skipped movies are replaced by the next ones.
        for tmdb_id in tmdb_ids:
            if len(movies) == count:
                break
            try:
                movie, _ = import_movie(tmdb_id)
            except TMDBClientError as e:
                self.stderr.write(self.style.WARNING(f"Skipped {tmdb_id}: {e}"))
                continue
            # Without a runtime there is no way to compute when the show ends.
            if movie.runtime is None:
                self.stderr.write(self.style.WARNING(f"Skipped {movie}: no runtime on TMDB"))
                continue
            movies.append(movie)
            self.stdout.write(f"Imported: {movie}")

        if not movies:
            raise CommandError("No movies could be imported, so nothing can be scheduled.")
        return movies

    def create_auditoriums(self):
        auditoriums = []
        for name, rows, columns in AUDITORIUMS:
            # get_or_create calls save(), which generates the seats of a new auditorium.
            auditorium, created = Auditorium.objects.get_or_create(
                name=name, defaults={"rows": rows, "columns": columns}
            )
            # Only on creation, so later changes made by staff in the admin are kept.
            if created:
                auditorium.seats.filter(row=1, number__in=[1, columns]).update(
                    seat_type=Seat.SeatType.WHEELCHAIR
                )
                self.stdout.write(f"Created: {auditorium} ({rows}x{columns})")
            auditoriums.append(auditorium)
        return auditoriums

    def schedule(self, auditoriums, movies, days):
        created = skipped = 0
        today = timezone.localdate()

        for day_index in range(days):
            day = today + timedelta(days=day_index)
            for auditorium_index, auditorium in enumerate(auditoriums):
                # Whole days are the unit: if the movies changed, new start times
                # would not line up with the ones already saved.
                if auditorium.showtimes.filter(starts_at__date=day).exists():
                    skipped += 1
                    continue

                # A different offset per day and auditorium spreads the movies around.
                offset = day_index * len(auditoriums) + auditorium_index
                for movie, starts_at in plan_day(day, movies, offset):
                    showtime = Showtime(
                        movie=movie,
                        auditorium=auditorium,
                        starts_at=starts_at,
                        base_price=price_for(starts_at),
                    )
                    # save() skips clean(), so the overlap rule is run explicitly.
                    showtime.full_clean()
                    showtime.save()
                    created += 1

        return created, skipped
