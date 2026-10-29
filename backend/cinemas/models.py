from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction

MAX_ROWS = 26
MAX_COLUMNS = 30


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
