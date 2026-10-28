from io import StringIO
from unittest import mock

import pytest
from django.core.management import CommandError, call_command

from movies.models import Movie
from movies.tmdb import TMDBClientError

# The command only orchestrates; the import logic is tested in test_importer.py.
# Here `import_movie` is replaced so these tests check the command alone.
IMPORT_MOVIE = "movies.management.commands.import_movies.import_movie"


def run(*ids):
    """Run the command and return what it printed to stdout and stderr."""
    out, err = StringIO(), StringIO()
    call_command("import_movies", *ids, stdout=out, stderr=err)
    return out.getvalue(), err.getvalue()


def test_imports_every_id():
    movie = Movie(tmdb_id=27205, title="Inception")

    with mock.patch(IMPORT_MOVIE, return_value=(movie, True)) as fake:
        out, _ = run("27205", "550")

    # argparse turned the strings into ints (`type=int`).
    assert [c.args for c in fake.call_args_list] == [(27205,), (550,)]
    assert out.count("Created: Inception") == 2


def test_reports_updated_movies():
    movie = Movie(tmdb_id=27205, title="Inception")

    with mock.patch(IMPORT_MOVIE, return_value=(movie, False)):
        out, _ = run("27205")

    assert "Updated: Inception (27205)" in out


def test_keeps_going_after_an_error_and_fails_at_the_end():
    movie = Movie(tmdb_id=550, title="Fight Club")
    results = [TMDBClientError("404 Not Found"), (movie, True)]
    out, err = StringIO(), StringIO()

    with mock.patch(IMPORT_MOVIE, side_effect=results):
        with pytest.raises(CommandError, match="Failed to import: 999"):
            call_command("import_movies", "999", "550", stdout=out, stderr=err)

    # The bad id is reported, and the next id is still imported.
    assert "999: 404 Not Found" in err.getvalue()
    assert "Created: Fight Club" in out.getvalue()


def test_requires_at_least_one_id():
    with pytest.raises(CommandError):
        call_command("import_movies")
