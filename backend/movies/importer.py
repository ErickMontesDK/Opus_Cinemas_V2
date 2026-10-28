"""Turn TMDB movie data into `Movie` and `Genre` rows.

The parsing helpers are pure functions (JSON in, values out) so they can be
tested without a database. `import_movie` is the only function that touches
TMDB and the database.
"""

from django.db import transaction
from django.utils.dateparse import parse_date

from .models import Genre, Movie
from .tmdb import fetch_movie_details

# The cinema is in Vancouver, so Canadian ratings come first; US is the fallback.
CLASSIFICATION_COUNTRIES = ("CA", "US")
# TMDB release type 3 means "Theatrical".
THEATRICAL_RELEASE = 3
YOUTUBE_URL = "https://www.youtube.com/watch?v={key}"


def extract_classification(data):
    """Return the age rating (for example "14A"), or "" if TMDB has none.

    Countries are tried in `CLASSIFICATION_COUNTRIES` order. Within a country,
    a theatrical release wins over other release types (premiere, DVD...).
    """
    results = data.get("release_dates", {}).get("results", [])
    by_country = {item["iso_3166_1"]: item["release_dates"] for item in results}

    for country in CLASSIFICATION_COUNTRIES:
        # Keep only releases that actually have a rating.
        releases = [r for r in by_country.get(country, []) if r.get("certification")]
        if not releases:
            continue
        # `False` sorts before `True`, so theatrical releases come first.
        releases.sort(key=lambda r: r.get("type") != THEATRICAL_RELEASE)
        return releases[0]["certification"]

    return ""


def extract_trailer(data):
    """Return the YouTube URL of the movie trailer, or "" if there is none.

    Only YouTube videos of type "Trailer" count. Official trailers win over
    unofficial ones; otherwise TMDB's order is kept.
    """
    videos = data.get("videos", {}).get("results", [])
    # Drop clips, featurettes and videos hosted outside YouTube.
    trailers = [t for t in videos if t.get("site") == "YouTube" and t.get("type") == "Trailer"]
    if not trailers:
        return ""

    # `not True` is False, and False sorts first, so official trailers come first.
    trailers.sort(key=lambda t: not t.get("official", False))
    return YOUTUBE_URL.format(key=trailers[0]["key"])


def parse_movie(data):
    """Map the TMDB JSON to the fields of our `Movie` model."""
    return {
        "title": data["title"],
        # TMDB sends `null` for missing text; our text fields use "" instead.
        "synopsis": data.get("overview") or "",
        # TMDB uses 0 or `null` when the runtime is unknown.
        "runtime": data.get("runtime") or None,
        # TMDB sends the date as a string ("" when unknown). Parse it, otherwise the
        # returned `movie` would hold a str instead of a `date` until reloaded.
        "release_date": parse_date(data.get("release_date") or "") or None,
        "poster_path": data.get("poster_path") or "",
        "backdrop_path": data.get("backdrop_path") or "",
        "classification": extract_classification(data),
        "trailer": extract_trailer(data),
    }


def import_movie(tmdb_id):
    """Fetch a movie from TMDB and create or update it in the database.

    Returns `(movie, created)`, like `update_or_create`. Raises
    `TMDBClientError` if TMDB cannot be reached or the id does not exist.
    """
    # Fetch and parse before opening the transaction, so a slow HTTP call
    # does not keep a database transaction open.
    data = fetch_movie_details(tmdb_id)
    fields = parse_movie(data)

    # All or nothing: a movie is never saved without its genres.
    with transaction.atomic():
        movie, created = Movie.objects.update_or_create(tmdb_id=data["id"], defaults=fields)
        genres = [
            Genre.objects.update_or_create(tmdb_id=g["id"], defaults={"name": g["name"]})[0]
            for g in data.get("genres", [])
        ]
        # `set()` adds missing genres and removes the ones TMDB no longer lists.
        movie.genres.set(genres)

    return movie, created
