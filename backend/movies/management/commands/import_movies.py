from django.core.management.base import BaseCommand, CommandError

from movies.importer import import_movie
from movies.tmdb import TMDBClientError


class Command(BaseCommand):
    help = "Import movies from TMDB by id, or update them if they already exist."

    def add_arguments(self, parser):
        # `nargs="+"` accepts one or more ids: `import_movies 27205 550`.
        parser.add_argument("tmdb_ids", nargs="+", type=int, help="TMDB movie ids")

    def handle(self, *args, **options):
        failed = []

        for tmdb_id in options["tmdb_ids"]:
            # One bad id must not stop the rest of the batch.
            try:
                movie, created = import_movie(tmdb_id)
            except TMDBClientError as e:
                failed.append(tmdb_id)
                self.stderr.write(self.style.ERROR(f"{tmdb_id}: {e}"))
                continue

            action = "Created" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(f"{action}: {movie} ({tmdb_id})"))

        # A non-zero exit code tells scripts (and the seed command) that something failed.
        if failed:
            raise CommandError(f"Failed to import: {', '.join(map(str, failed))}")
