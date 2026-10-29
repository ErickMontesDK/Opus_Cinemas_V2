# Learning log

A short entry per roadmap step: what was built, the key decisions and the concepts learned.

---

## 2.6 Showtimes

**Built**
- `Showtime` model (movie, auditorium, starts_at, ends_at, base_price) with admin registration (date hierarchy, movie autocomplete, read-only `ends_at`).
- Overlap validation in `clean()`: no two showtimes in the same auditorium can share any time.
- Tests for `ends_at`, the overlap cases, back-to-back showtimes, editing, a missing runtime and a negative price.

**Key decisions**
- `ends_at` is stored and computed (`starts_at + runtime + CLEANING_MINUTES`) in both `save()` and `clean()`, because forms validate before saving.
- A movie without a runtime is rejected instead of using a default duration, which would produce a wrong `ends_at`.
- Overlap rule in `clean()` only (the simple option). Trade-off: `objects.create()`, `save()` and scripts skip it, and two concurrent requests could both pass. The stronger alternative is a Postgres `ExclusionConstraint` on a `tstzrange` with the `btree_gist` extension.
- `on_delete=PROTECT` on movie and auditorium: deleting them must not silently delete showtimes (and, later, sold tickets).
- `base_price` is a `DecimalField` with a validator plus a `CheckConstraint` (not negative).

**Concepts**
- `clean()` only runs through `full_clean()`: model forms and the admin call it, but `save()`, `objects.create()` and DRF serializers do not.
- Two ranges overlap when `a.start < b.end and a.end > b.start`. Strict comparisons allow a showtime to start exactly when the previous one ends.
- `exclude(pk=self.pk)` so an edited object does not conflict with itself.
- `editable=False` hides a field from forms and skips its validation in `full_clean()`.
- Datetimes are stored in UTC; `timezone.localtime()` converts them to `America/Vancouver` for display.
- A test that proves "this is allowed" needs the conflicting data to exist; otherwise it passes even when the rule is broken.

---

## 2.5 Auditoriums and seats

**Built**
- `Auditorium` (name, rows, columns) and `Seat` (auditorium, row, number, seat_type) models in the `cinemas` app, with migration and admin.
- `Auditorium.save()` generates one seat per `(row, number)` position when the auditorium is created.
- Tests for seat generation, labels, defaults and the database constraints.

**Key decisions**
- Rows are stored as integers and shown as letters (`row_label`, `label` such as "A5"): integers sort correctly and map directly to the seat map grid.
- Seats are generated in `save()`, not in a signal or an explicit method, so they exist whatever creates the auditorium (admin, shell, seed). Trade-off: `Auditorium.objects.bulk_create()` skips `save()` and would create auditoriums without seats.
- Dimensions are fixed after creation (read-only in the admin), because resizing would leave seats and future tickets out of sync.
- `seat_type` is a `TextChoices` field (standard, wheelchair), not a separate model: prices come from ticket types, not seats.
- Limits of 26 rows (A to Z) and 30 columns.

**Concepts**
- Validators only run in `full_clean()` (model forms, DRF model serializers) and give a clear error message; `CheckConstraint` and `UniqueConstraint` are enforced by Postgres for every write.
- `self._state.adding` tells whether the object has been inserted yet; it must be read before `super().save()`.
- `transaction.atomic()` makes the auditorium and its seats all or nothing.
- `bulk_create` inserts many rows in one query, but does not call each object's `save()` or send `pre_save`/`post_save` signals.
- `pytest.mark.parametrize` runs one test with several inputs (boundary values 0 and 27).

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
