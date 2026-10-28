# Learning log

A short entry per roadmap step: what was built, the key decisions and the concepts learned.

---

## 2.4 Import from TMDB

**Built**
- `movies/importer.py`: turns TMDB JSON into `Movie` and `Genre` rows. Pure helpers (`extract_classification`, `extract_trailer`, `parse_movie`) plus `import_movie(tmdb_id)`, which fetches, parses and saves.
- `import_movies` management command: `python manage.py import_movies 27205 550`.
- Tests for the parsing rules, the database writes and the command.

**Key decisions**
- A management command, not an admin action: an admin action only works on rows that already exist, and the seed command (2.10) can reuse the importer.
- The import logic lives in its own module, separate from the HTTP client (`tmdb.py`) and the CLI (the command). Each file has one reason to change.
- No DRF serializer for TMDB data: the mapping is not field to field, upserts and nested M2M writes are not built in, and TMDB's format should stay separate from our own API contract. Trade-off: no field validation before saving.
- Classification: Canadian rating first (the cinema is in Vancouver), US as the fallback, theatrical release preferred.
- Trailer: YouTube videos of type "Trailer", official ones first, TMDB's order otherwise.
- A failing id does not stop the batch; the command exits with an error at the end.

**Concepts**
- Idempotency with `update_or_create`, backed by the `unique=True` constraint on `tmdb_id`.
- `transaction.atomic()` makes the movie and its genres all or nothing. Keep transactions short: the HTTP call stays outside.
- `movie.genres.set()` syncs a many-to-many relation (adds and removes), unlike `add()`.
- Sorting by a boolean key (`False` sorts first) with Python's stable sort to express "prefer X".
- `mock.patch` replaces a name: patch where it is used (`movies.importer.fetch_movie_details`), not where it is defined.
- Normalising missing external values (`null`, `0`, `""`) and parsing dates with `parse_date`, so the returned object holds a `date`, not a `str`.
