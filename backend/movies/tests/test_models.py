import pytest
from django.db import IntegrityError, transaction

from movies.models import Genre, Movie


@pytest.fixture
def genre(db):
    return Genre.objects.create(tmdb_id=3, name="Action")


@pytest.fixture
def movie(db):
    return Movie.objects.create(tmdb_id=1, title="Inception")


def test_genre_str_is_name(genre):
    assert str(genre) == "Action"


def test_genre_unique_tmdb_id(genre):
    with pytest.raises(IntegrityError), transaction.atomic():
        Genre.objects.create(tmdb_id=3, name="Comedy")

    assert Genre.objects.count() == 1


def test_genre_unique_name(genre):
    with pytest.raises(IntegrityError), transaction.atomic():
        Genre.objects.create(tmdb_id=4, name="Action")

    assert Genre.objects.count() == 1


def test_movie_str_is_title(movie):
    assert str(movie) == "Inception"


def test_movie_unique_tmdb_id(movie):
    with pytest.raises(IntegrityError), transaction.atomic():
        Movie.objects.create(tmdb_id=1, title="Interstellar")

    assert Movie.objects.count() == 1


def test_genre_ordered_by_name(db):
    genre1 = Genre.objects.create(tmdb_id=1, name="Comedy")
    genre2 = Genre.objects.create(tmdb_id=2, name="Action")
    genre3 = Genre.objects.create(tmdb_id=3, name="Drama")

    genres = list(Genre.objects.all())
    assert genres == [genre2, genre1, genre3]  # Ordered by name


def test_movie_ordered_by_title(db):
    movie1 = Movie.objects.create(tmdb_id=1, title="Inception")
    movie2 = Movie.objects.create(tmdb_id=2, title="Avatar")
    movie3 = Movie.objects.create(tmdb_id=3, title="The Dark Knight")

    movies = list(Movie.objects.all())
    assert movies == [movie2, movie1, movie3]  # Ordered by title


def test_default_values(db):
    movie = Movie.objects.create(tmdb_id=1, title="Inception")

    assert movie.synopsis == ""
    assert movie.runtime is None
    assert movie.classification == ""
    assert movie.release_date is None
    assert movie.poster_path == ""
    assert movie.backdrop_path == ""
    assert movie.trailer == ""


def test_genre_movie_relationship(db):
    genre = Genre.objects.create(tmdb_id=1, name="Action")
    movie = Movie.objects.create(tmdb_id=1, title="Inception")

    movie.genres.add(genre)

    assert genre in movie.genres.all()
    assert movie in genre.movies.all()
