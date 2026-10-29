import pytest
from django.db import IntegrityError, transaction

from cinemas.models import Auditorium, Seat


@pytest.fixture
def auditorium(db):
    # A small 3 x 4 auditorium: rows A to C, seats 1 to 4.
    return Auditorium.objects.create(name="Auditorium 1", rows=3, columns=4)


def test_auditorium_str_is_name(auditorium):
    assert str(auditorium) == "Auditorium 1"


def test_creating_auditorium_generates_all_seats(auditorium):
    assert auditorium.seats.count() == 3 * 4


def test_generated_seats_cover_the_whole_grid(auditorium):
    seats = list(auditorium.seats.all())  # Ordered by row, then number

    assert seats[0].label == "A1"
    assert seats[-1].label == "C4"


def test_row_label_converts_row_to_letter(auditorium):
    assert Seat(auditorium=auditorium, row=1, number=1).row_label == "A"
    assert Seat(auditorium=auditorium, row=26, number=1).row_label == "Z"


def test_seat_str_includes_auditorium_and_label(auditorium):
    seat = auditorium.seats.get(row=2, number=3)

    assert str(seat) == "Auditorium 1 · B3"


def test_seat_type_defaults_to_standard(auditorium):
    assert not auditorium.seats.exclude(seat_type=Seat.SeatType.STANDARD).exists()


def test_seat_position_is_unique(auditorium):
    with pytest.raises(IntegrityError), transaction.atomic():
        Seat.objects.create(auditorium=auditorium, row=1, number=1)

    assert auditorium.seats.count() == 12


@pytest.mark.parametrize("rows", [0, 27])
def test_rows_out_of_range_rejected_by_database(db, rows):
    with pytest.raises(IntegrityError), transaction.atomic():
        Auditorium.objects.create(name="Too big", rows=rows, columns=4)

    # The transaction rolled back: no auditorium and no seats were left behind.
    assert not Auditorium.objects.exists()
    assert not Seat.objects.exists()


@pytest.mark.parametrize("columns", [0, 31])
def test_columns_out_of_range_rejected_by_database(db, columns):
    with pytest.raises(IntegrityError), transaction.atomic():
        Auditorium.objects.create(name="Too wide", rows=3, columns=columns)

    assert not Auditorium.objects.exists()


def test_saving_existing_auditorium_does_not_duplicate_seats(auditorium):
    auditorium.name = "New name"
    auditorium.save()

    assert auditorium.seats.count() == 3 * 4
