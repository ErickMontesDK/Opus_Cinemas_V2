import pytest
from django.urls import reverse

from movies.models import Genre, Movie


@pytest.fixture
def movie(db):
    movie = Movie.objects.create(
        tmdb_id=27205,
        title="Inception",
        synopsis="A thief who steals corporate secrets through dreams.",
        runtime=148,
        classification="PG",
        poster_path="/inception.jpg",
        trailer="https://www.youtube.com/watch?v=YoHD9XEInc0",
    )
    movie.genres.add(
        Genre.objects.create(tmdb_id=28, name="Action"),
        Genre.objects.create(tmdb_id=878, name="Science Fiction"),
    )
    return movie


def test_movie_list_returns_light_fields(client, movie):
    response = client.get(reverse("movie-list"))

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": movie.id,
            "title": "Inception",
            "poster_path": "/inception.jpg",
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
    Movie.objects.create(tmdb_id=550, title="Fight Club").genres.add(*movie.genres.all())

    # One query for the movies and one for all their genres (prefetch_related).
    with django_assert_num_queries(2):
        client.get(reverse("movie-list"))
