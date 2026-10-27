import requests
from django.conf import settings

BASE_URL = "https://api.themoviedb.org/3"


class TMDBClientError(Exception):
    """Custom exception for TMDBClient errors."""

    pass


def fetch_movie_details(tmdb_id):
    """Fetch movie details from TMDB API."""
    if not settings.TMDB_API_TOKEN:
        raise TMDBClientError("TMDB_API_TOKEN is not set")

    url = f"{BASE_URL}/movie/{tmdb_id}"
    headers = {
        "Authorization": f"Bearer {settings.TMDB_API_TOKEN}",
        "Accept": "application/json",
    }
    try:
        response = requests.get(
            url, headers=headers, timeout=10, params={"append_to_response": "release_dates,videos"}
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise TMDBClientError(f"Error fetching movie details: {e}") from e
