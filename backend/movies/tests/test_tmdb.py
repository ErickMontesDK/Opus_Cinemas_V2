import json
from pathlib import Path
from unittest import mock

import pytest
import requests

from movies.tmdb import BASE_URL, TMDBClientError, fetch_movie_details

FIXTURE = Path(__file__).parent / "fixtures" / "tmdb_movie_27205.json"


@pytest.fixture(autouse=True)
def tmdb_token(settings):
    settings.TMDB_API_TOKEN = "test-token"


@pytest.fixture
def movie_data():
    return json.loads(FIXTURE.read_text())


def fake_response(data=None, status_error=None):
    """Build an object that behaves like a `requests.Response`."""
    response = mock.Mock(spec=requests.Response)
    response.json.return_value = data
    if status_error:
        response.raise_for_status.side_effect = status_error
    return response


def test_returns_movie_data(movie_data):
    with mock.patch("movies.tmdb.requests.get", return_value=fake_response(movie_data)):
        result = fetch_movie_details(27205)

    assert result == movie_data


def test_sends_url_token_and_extra_endpoints(movie_data):
    with mock.patch("movies.tmdb.requests.get", return_value=fake_response(movie_data)) as mock_get:
        fetch_movie_details(27205)

    # `call_args` records how our code called `requests.get`.
    args, kwargs = mock_get.call_args
    assert args[0] == f"{BASE_URL}/movie/27205"
    assert kwargs["headers"]["Authorization"] == "Bearer test-token"
    assert kwargs["params"] == {"append_to_response": "release_dates,videos"}
    assert kwargs["timeout"] == 10


def test_missing_token_raises_without_calling_tmdb(settings):
    settings.TMDB_API_TOKEN = ""

    with mock.patch("movies.tmdb.requests.get") as mock_get:
        with pytest.raises(TMDBClientError, match="TMDB_API_TOKEN is not set"):
            fetch_movie_details(27205)

    mock_get.assert_not_called()


def test_http_error_raises_client_error():
    error = requests.HTTPError("404 Client Error: Not Found")

    with mock.patch("movies.tmdb.requests.get", return_value=fake_response(status_error=error)):
        with pytest.raises(TMDBClientError, match="404"):
            fetch_movie_details(999999999)


def test_network_error_raises_client_error():
    with mock.patch("movies.tmdb.requests.get", side_effect=requests.Timeout("timed out")):
        with pytest.raises(TMDBClientError) as excinfo:
            fetch_movie_details(27205)

    # `raise ... from e` keeps the original error as the cause.
    assert isinstance(excinfo.value.__cause__, requests.Timeout)
