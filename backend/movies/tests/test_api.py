from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.urls import reverse
from django.utils import timezone

from cinemas.models import Auditorium, Showtime
from movies.models import Genre, Movie


def schedule(movie, hours_from_now):
    """Give a movie one showtime, in the past when `hours_from_now` is negative."""
    auditorium, _ = Auditorium.objects.get_or_create(
        name="Room", defaults={"rows": 1, "columns": 1}
    )
    return Showtime.objects.create(
        movie=movie,
        auditorium=auditorium,
        starts_at=timezone.now() + timedelta(hours=hours_from_now),
        base_price=Decimal("14.00"),
    )


@pytest.fixture
def movie(db):
    movie = Movie.objects.create(
        tmdb_id=27205,
        title="Inception",
        synopsis="A thief who steals corporate secrets through dreams.",
        runtime=148,
        classification="PG",
        poster_path="/inception.jpg",
        backdrop_path="/inception-backdrop.jpg",
        release_date=date(2010, 7, 16),
        trailer="https://www.youtube.com/watch?v=YoHD9XEInc0",
    )
    movie.genres.add(
        Genre.objects.create(tmdb_id=28, name="Action"),
        Genre.objects.create(tmdb_id=878, name="Science Fiction"),
    )
    return movie


def test_movie_list_returns_light_fields(client, movie):
    schedule(movie, hours_from_now=2)

    response = client.get(reverse("movie-list"))

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": movie.id,
            "title": "Inception",
            "poster_path": "/inception.jpg",
            "backdrop_path": "/inception-backdrop.jpg",
            "release_date": "2010-07-16",
            "classification": "PG",
            "runtime": 148,
            "genres": ["Action", "Science Fiction"],
        }
    ]


def test_movie_detail_returns_all_fields(client, movie):
    response = client.get(reverse("movie-detail", args=[movie.id]))

    assert response.status_code == 200
    data = response.json()
    assert data["synopsis"] == movie.synopsis
    assert data["trailer"] == movie.trailer
    assert data["genres"] == ["Action", "Science Fiction"]


@pytest.mark.django_db
def test_movie_detail_returns_404_for_unknown_id(client):
    response = client.get(reverse("movie-detail", args=[999]))

    assert response.status_code == 404


def test_movie_list_query_count_does_not_grow_with_movies(client, movie, django_assert_num_queries):
    other = Movie.objects.create(tmdb_id=550, title="Fight Club", runtime=139)
    other.genres.add(*movie.genres.all())
    schedule(movie, hours_from_now=2)
    schedule(other, hours_from_now=6)

    # One query for the movies and one for all their genres (prefetch_related).
    with django_assert_num_queries(2):
        client.get(reverse("movie-list"))


def test_movie_list_hides_movies_without_upcoming_showtimes(client, movie):
    past = Movie.objects.create(tmdb_id=550, title="Fight Club", runtime=139)
    Movie.objects.create(tmdb_id=603, title="The Matrix", runtime=136)
    schedule(past, hours_from_now=-48)
    schedule(movie, hours_from_now=2)

    response = client.get(reverse("movie-list"))

    assert [m["title"] for m in response.json()] == ["Inception"]


def test_movie_list_shows_a_movie_once_with_many_showtimes(client, movie):
    for hours in (2, 6, 30):
        schedule(movie, hours_from_now=hours)

    response = client.get(reverse("movie-list"))

    # Without distinct() the join would return Inception three times.
    assert len(response.json()) == 1


def test_movie_detail_works_without_upcoming_showtimes(client, movie):
    response = client.get(reverse("movie-detail", args=[movie.id]))

    assert response.status_code == 200
