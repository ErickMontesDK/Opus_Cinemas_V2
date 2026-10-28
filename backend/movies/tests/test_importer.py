import copy
import datetime
import json
from pathlib import Path
from unittest import mock

import pytest

from movies.importer import extract_classification, extract_trailer, import_movie
from movies.models import Genre, Movie

FIXTURE = Path(__file__).parent / "fixtures" / "tmdb_movie_27205.json"


@pytest.fixture
def movie_data():
    return json.loads(FIXTURE.read_text())


def release(certification, type_=3):
    """Build one entry of TMDB's `release_dates` list."""
    return {"certification": certification, "type": type_}


def with_releases(**countries):
    """Build the `release_dates` block, e.g. `with_releases(US=[release("R")])`."""
    results = [{"iso_3166_1": c, "release_dates": r} for c, r in countries.items()]
    return {"release_dates": {"results": results}}


def video(key, site="YouTube", type_="Trailer", official=True):
    """Build one entry of TMDB's `videos` list."""
    return {"key": key, "site": site, "type": type_, "official": official}


def with_videos(*videos):
    return {"videos": {"results": list(videos)}}


# --- extract_classification -------------------------------------------------


def test_classification_prefers_canada(movie_data):
    # Inception is rated 14A in Canada and PG-13 in the US.
    assert extract_classification(movie_data) == "14A"


def test_classification_falls_back_to_us():
    data = with_releases(FR=[release("12")], US=[release("PG-13")])

    assert extract_classification(data) == "PG-13"


def test_classification_skips_empty_certifications():
    # Canada is listed but has no rating, so the US one is used.
    data = with_releases(CA=[release("")], US=[release("R")])

    assert extract_classification(data) == "R"


def test_classification_prefers_theatrical_release():
    # Type 1 is a premiere, type 3 the theatrical release.
    data = with_releases(CA=[release("PG", type_=1), release("14A", type_=3)])

    assert extract_classification(data) == "14A"


def test_classification_is_empty_when_missing():
    assert extract_classification({}) == ""


# --- extract_trailer (Erick's function) ---------------------------------------


def test_trailer_from_fixture(movie_data):
    # The fixture lists an unofficial trailer first; the first official one wins.
    assert extract_trailer(movie_data) == "https://www.youtube.com/watch?v=JE9z-gy4De4"


def test_trailer_prefers_official():
    data = with_videos(video("fan", official=False), video("studio", official=True))

    assert extract_trailer(data) == "https://www.youtube.com/watch?v=studio"


def test_trailer_ignores_other_sites_and_types():
    data = with_videos(
        video("vimeo1", site="Vimeo"),
        video("clip1", type_="Clip"),
        video("real", official=False),
    )

    assert extract_trailer(data) == "https://www.youtube.com/watch?v=real"


def test_trailer_is_empty_when_missing():
    assert extract_trailer(with_videos(video("clip1", type_="Clip"))) == ""
    assert extract_trailer({}) == ""


# --- import_movie -------------------------------------------------------------


def run_import(data):
    """Run `import_movie` with TMDB replaced by `data`."""
    # Patch the name where it is used (`movies.importer`), not where it is defined.
    with mock.patch("movies.importer.fetch_movie_details", return_value=data) as fake:
        result = import_movie(data["id"])
    fake.assert_called_once_with(data["id"])
    return result


@pytest.mark.django_db
def test_import_creates_movie(movie_data):
    movie, created = run_import(movie_data)

    assert created is True
    assert movie.tmdb_id == 27205
    assert movie.title == "Inception"
    assert movie.runtime == 148
    assert movie.release_date == datetime.date(2010, 7, 15)
    assert movie.poster_path == movie_data["poster_path"]
    assert movie.classification == "14A"
    assert movie.synopsis.startswith("Cobb")


@pytest.mark.django_db
def test_import_creates_and_links_genres(movie_data):
    movie, _ = run_import(movie_data)

    names = set(movie.genres.values_list("name", flat=True))
    assert names == {"Action", "Science Fiction", "Crime"}


@pytest.mark.django_db
def test_reimport_updates_instead_of_duplicating(movie_data):
    run_import(movie_data)

    changed = copy.deepcopy(movie_data)
    changed["title"] = "Inception (Re-release)"
    changed["genres"] = [{"id": 28, "name": "Action"}]
    movie, created = run_import(changed)

    assert created is False
    assert Movie.objects.count() == 1
    assert movie.title == "Inception (Re-release)"
    # Genres TMDB no longer lists are unlinked from the movie...
    assert list(movie.genres.values_list("name", flat=True)) == ["Action"]
    # ...but the Genre rows stay, other movies may use them.
    assert Genre.objects.count() == 3


@pytest.mark.django_db
def test_import_handles_missing_values(movie_data):
    data = copy.deepcopy(movie_data)
    data.update(overview=None, runtime=0, release_date="", poster_path=None)

    movie, _ = run_import(data)

    assert movie.synopsis == ""
    assert movie.runtime is None
    assert movie.release_date is None
    assert movie.poster_path == ""
