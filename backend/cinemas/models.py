from datetime import timedelta

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction
from django.utils import timezone

MAX_ROWS = 26
MAX_COLUMNS = 30
# Minutes after each showtime to clean the auditorium before the next one.
CLEANING_MINUTES = 15


class Auditorium(models.Model):
    name = models.CharField(max_length=100, unique=True)
    # Validators give a clear error in admin forms (they only run in full_clean()).
    # The CheckConstraints in Meta enforce the same limits in Postgres for every write.
    rows = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(MAX_ROWS)]
    )
    columns = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(MAX_COLUMNS)]
    )

    class Meta:
        ordering = ["name"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(rows__gte=1, rows__lte=MAX_ROWS),
                name="auditorium_rows_in_range",
            ),
            models.CheckConstraint(
                condition=models.Q(columns__gte=1, columns__lte=MAX_COLUMNS),
                name="auditorium_columns_in_range",
            ),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # _state.adding is True only before the first INSERT, so it is read before
        # super().save(). Seats are generated once, when the auditorium is created;
        # later saves (e.g. a rename) skip it.
        is_new = self._state.adding
        # The auditorium and its seats are saved all or nothing.
        with transaction.atomic():
            super().save(*args, **kwargs)
            if is_new:
                self._generate_seats()

    def _generate_seats(self):

        seats = [
            Seat(auditorium=self, row=row, number=number)
            for row in range(1, self.rows + 1)
            for number in range(1, self.columns + 1)
        ]
        Seat.objects.bulk_create(seats)


class Seat(models.Model):
    class SeatType(models.TextChoices):
        STANDARD = "standard", "Standard"
        WHEELCHAIR = "wheelchair", "Wheelchair space"

    auditorium = models.ForeignKey(Auditorium, on_delete=models.CASCADE, related_name="seats")
    row = models.PositiveSmallIntegerField()
    number = models.PositiveSmallIntegerField()
    seat_type = models.CharField(max_length=20, choices=SeatType.choices, default=SeatType.STANDARD)

    class Meta:
        ordering = ["auditorium", "row", "number"]
        constraints = [
            models.UniqueConstraint(
                fields=["auditorium", "row", "number"],
                name="unique_seat_position",
            ),
        ]

    def __str__(self):
        return f"{self.auditorium} · {self.label}"

    @property
    def row_label(self):
        # 1 -> "A", 2 -> "B", ... 26 -> "Z".
        return chr(ord("A") + self.row - 1)

    @property
    def label(self):
        return f"{self.row_label}{self.number}"


class Showtime(models.Model):
    # PROTECT: a movie or auditorium with showtimes cannot be deleted by accident.
    movie = models.ForeignKey("movies.Movie", on_delete=models.PROTECT, related_name="showtimes")
    auditorium = models.ForeignKey(Auditorium, on_delete=models.PROTECT, related_name="showtimes")
    starts_at = models.DateTimeField()
    # Computed in save() from starts_at, the movie runtime and the cleaning time.
    ends_at = models.DateTimeField(editable=False)
    base_price = models.DecimalField(
        max_digits=6, decimal_places=2, validators=[MinValueValidator(0)]
    )

    class Meta:
        ordering = ["starts_at"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(base_price__gte=0),
                name="showtime_base_price_not_negative",
            ),
        ]

    def __str__(self):
        starts_at = timezone.localtime(self.starts_at)
        return f"{self.movie} · {self.auditorium} · {starts_at:%Y-%m-%d %H:%M}"

    def save(self, *args, **kwargs):
        self.ends_at = self._compute_ends_at()
        super().save(*args, **kwargs)

    def clean(self):
        # Only runs through full_clean() (admin forms), not on save() or objects.create().
        super().clean()

        # A required field failed its own validation and already shows its error.
        if self.movie_id is None or self.auditorium_id is None or self.starts_at is None:
            return

        # Forms validate before save(), so ends_at is not set yet.
        self.ends_at = self._compute_ends_at()

        # Strict < and > let a showtime start exactly when the previous one ends.
        overlapping = (
            Showtime.objects.filter(
                auditorium_id=self.auditorium_id,
                starts_at__lt=self.ends_at,
                ends_at__gt=self.starts_at,
            )
            .exclude(pk=self.pk)  # An edited showtime must not clash with itself
            .first()
        )
        if overlapping is not None:
            raise ValidationError({"starts_at": f"Overlaps with {overlapping}."})

    def _compute_ends_at(self):
        if self.movie.runtime is None:
            raise ValidationError(
                {"movie": "This movie has no runtime. Set it in the movie admin first."}
            )
        return self.starts_at + timedelta(minutes=self.movie.runtime + CLEANING_MINUTES)
