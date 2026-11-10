import requests
from django.conf import settings

BASE_URL = "https://api.themoviedb.org/3"


class TMDBClientError(Exception):
    """Custom exception for TMDBClient errors."""

    pass


def _get(path, params=None):
    """Send an authenticated GET request to TMDB and return the JSON body."""
    if not settings.TMDB_API_TOKEN:
        raise TMDBClientError("TMDB_API_TOKEN is not set")

    headers = {
        "Authorization": f"Bearer {settings.TMDB_API_TOKEN}",
        "Accept": "application/json",
    }
    try:
        response = requests.get(f"{BASE_URL}{path}", headers=headers, timeout=10, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise TMDBClientError(f"Error fetching {path}: {e}") from e


def fetch_movie_details(tmdb_id):
    """Fetch movie details from TMDB API."""
    return _get(f"/movie/{tmdb_id}", params={"append_to_response": "release_dates,videos"})


def fetch_now_playing(region="CA"):
    """Return the TMDB ids of the movies now in theaters, in TMDB's order.

    The list endpoint has no runtime, so callers import each id with its details.
    """
    data = _get("/movie/now_playing", params={"region": region})
    return [movie["id"] for movie in data.get("results", [])]
