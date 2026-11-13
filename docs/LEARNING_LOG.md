# Learning log

A short entry per roadmap step: what was built, the key decisions and the concepts learned.

---

## 2.9 Movie page

**Built**
- `/movies/[id]`: a Server Component with the poster, title, tags, release date, YouTube trailer and synopsis, plus a showtimes panel with one tab per day.
- `generateMetadata` sets the page title and description; the root layout adds a title template (`%s · Opus Cinemas`).
- `getMovie()`, `getShowtimes()` and the `MovieDetail` and `Showtime` types in `lib/api.ts`; `backdropUrl()` in `lib/tmdb.ts`; `trailerEmbedUrl()` in `lib/youtube.ts`; date formatters and `groupShowtimesByDate()` in `lib/format.ts`.
- `MovieMetaTags`, `TrailerEmbed` and `ShowtimeTabs` components in `components/movie/`.
- Movie cards on the listing now link to the movie page.
- The look follows v1 (blurred backdrop, glass panels, pill tags, time grid), rebuilt mobile first with Tailwind tokens.

**Key decisions**
- Day tabs are links (`?date=YYYY-MM-DD`) read from `searchParams`, not `useState`: they can be shared, survive a reload and the back button, and keep the page a Server Component. Trade-off: each tab change is a server round trip.
- Tabs come from the days that have showtimes (v1 had fixed "Today / Tomorrow / After Tomorrow" tabs). A missing or unknown date falls back to the first day.
- Showtimes are grouped by day in the frontend: it is presentation, and the API keeps a flat list that other screens can reuse.
- `getMovie()` is wrapped in React's `cache()`, because Next does not dedupe a `fetch` that has a `signal`, and `generateMetadata` and the page both need the movie.
- `getMovie()` only accepts digits, so an id like `../health` cannot reach another endpoint, and invalid ids return a 404 without calling the API.
- A missing movie returns `null` and the page calls `notFound()`; any other API error is thrown and caught by `error.tsx`.
- The synopsis sits next to the poster, above the trailer, so it is readable without scrolling; it stays left-aligned on mobile because centered paragraphs are hard to read.
- The trailer uses `youtube-nocookie.com`, `loading="lazy"` and a `title` for screen readers. Showtimes are not links yet: seat selection comes in phase 4.

**Concepts**
- Dynamic segments (`[id]`), and `params` and `searchParams` as Promises in Next 15+; the generated `PageProps<"/movies/[id]">` type.
- `notFound()` returns `never`, so TypeScript narrows `movie` to non-null after it.
- A page that reads `params` or `searchParams` is dynamic without `connection()`.
- Instants vs calendar days: `starts_at` is formatted in `America/Vancouver`; a date-only string (`"2026-11-06"`) becomes midnight UTC in `new Date()`, so it is formatted in UTC to stay on the same day. Offsets are never hardcoded; the time zone database decides them.
- `Intl.DateTimeFormat`, with the `en-CA` locale to get `YYYY-MM-DD` keys.
- Grouping with a `Record`, `??=` (nullish assignment), `Object.entries()` and sorting ISO dates as strings; `??` for fallbacks.
- Tailwind: opacity modifiers (`bg-ink/60`), arbitrary values (`lg:grid-cols-[3fr_2fr]`), `group`/`group-hover:`, `isolate` with negative `z-index`, `bg-radial`.
- `next/image` with `fill` for a background image, and `alt=""` for decorative images.
- State that should survive a shared link belongs in the URL; short-lived UI state (a form draft, an open menu) belongs in `useState`.

---

## 2.8 Listing page

**Built**
- The home page (`/`) is now the movie listing: a Server Component that fetches `GET /api/movies/` and renders a responsive grid of `MovieCard` components.
- `MovieCard` shows the poster with `next/image` (or a placeholder with the title), classification, genres and runtime.
- `getMovies()` and the `MovieListItem` type in `lib/api.ts`, `posterUrl()` in `lib/tmdb.ts`, `formatRuntime()` in `lib/format.ts`.
- `app/error.tsx` shows a fallback page with a "Try again" button when the API fails.
- The API status indicator from step 1.5 and `getApiHealth()` were removed; `/api/health/` stays in the backend.

**Key decisions**
- The listing lives at `/`, not `/movies`: the listing is the main page of a cinema.
- `getMovies()` throws on failure and `error.tsx` catches it, instead of returning `null` and handling errors in every page.
- Dynamic rendering with `connection()`: the listing changes, and the API is not reachable during `npm run build` in CI. ISR can be revisited at deploy time.
- The poster URL is built in the frontend: the image size is a presentation detail, not a business rule.
- Cards do not link to the movie page yet; the link comes with the route in step 2.9.

**Concepts**
- A TypeScript type that mirrors a DRF serializer catches mismatches at build time, but does not validate the response at runtime.
- `fetch` only throws on network errors, so `response.ok` must be checked by hand.
- Union types (`string | null`, `number | null`) and narrowing with `if (x === null)`.
- `next/image`: `width`/`height` reserve space (no layout shift), `sizes` lets phones download a smaller file, `preload` (replaces `priority` in Next 16) speeds up the first posters, and `remotePatterns` allow-lists external hosts.
- Mobile first in Tailwind: unprefixed classes apply to every screen, `sm:`/`lg:`/`xl:` override from that width up.
- JSX conditionals: `a ? b : c` and `a && b`; `.map()` with a stable `key`.
- Error boundaries need state and event handlers, so `error.tsx` must be a Client Component; in production the browser only gets a generic message and a `digest`.

---

## 2.7 Read API

**Built**
- `GET /api/movies/` and `GET /api/movies/{id}/` with a `ReadOnlyModelViewSet` and a `DefaultRouter`.
- `GET /api/showtimes/` with a `ListAPIView`: upcoming showtimes only, optional `?movie=<id>` and `?date=YYYY-MM-DD` filters.
- Each app has its own `urls.py`, included under `api/` in `config/urls.py`.
- API tests for both endpoints, including the response shape, a 404, the query count, the filters and invalid parameters.

**Key decisions**
- Two movie serializers: a light one for the list and a detail one that extends it, picked in `get_serializer_class()`.
- Genres as a list of names (`SlugRelatedField`), posters as TMDB paths so the frontend picks the image size.
- Showtimes get their own endpoint in `cinemas`, not a nested action under `movies`, because the model lives there.
- Past showtimes are filtered on the server: the client never decides what can be booked.
- The list shows every movie for now; step 2.10 limits it to movies with upcoming showtimes.
- Filters are written by hand in `get_queryset()` and documented with `@extend_schema`, instead of adding `django-filter` for two parameters.
- No pagination yet. Trade-off: adding it later changes the shape of the JSON.

**Concepts**
- `self.action` tells a viewset which action is running (`list`, `retrieve`); the router sets it.
- drf-spectacular reads the code without running it, so query parameters read inside `get_queryset()` must be declared with `OpenApiParameter`.
- DRF's `ValidationError` becomes a 400; an unhandled error in a view becomes a 500.
- `parse_date` fails in two ways: it raises `ValueError` for an impossible date and returns `None` for a string that is not a date. `starts_at__date=None` becomes `IS NULL` and silently returns an empty list.
- The `__date` lookup converts to the current time zone first, so 23:30 in Vancouver stays on its local day even though it is the next day in UTC.
- N+1 queries: `select_related` joins a foreign key in the same query; `prefetch_related` loads a many-to-many relation in one extra query with `IN (...)`. `django_assert_num_queries` guards against regressions.
- Tests use dates relative to `timezone.localdate()`, so they do not break when a fixed date passes or when UTC and Vancouver are on different days.

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

---

## 2.10 Seed data

**Built**
- `fetch_now_playing()` in `movies/tmdb.py`, sharing a `_get()` helper with `fetch_movie_details()`.
- `update_listing` management command (`cinemas`): creates three auditoriums (with two wheelchair spaces each), imports the movies now in theaters in Canada and schedules showtimes from today for `--days` days (default 7) with `--movies` movies (default 6).
- The movie list API only returns movies with upcoming showtimes; the detail endpoint still returns any movie.
- Fix on the movie page: the date tabs no longer widen the page on mobile, and the tab bar has a thin brand-colored scrollbar.

**Key decisions**
- One command both seeds an empty database and refreshes the listing later, instead of two commands sharing code.
- Movies come from TMDB `now_playing` (region `CA`). The list has no runtime, so every id is imported with its details; movies that fail or have no runtime are skipped and replaced by the next ones.
- Idempotency per auditorium and local day: a day that already has showtimes is left alone. Matching exact start times would break when the movies change, because new runtimes give new times.
- Network calls run before the transaction; auditoriums and showtimes are saved in one `transaction.atomic()`.
- Each showtime runs `full_clean()` before `save()`, so the overlap rule in `Showtime.clean()` also protects the command.
- Matinee price before 17:00, evening price after, using local time.

**Concepts**
- Custom management commands: `<app>/management/commands/<name>.py`, `add_arguments`, `CommandError`.
- `timezone.make_aware(datetime.combine(day, time))` builds a local datetime with the right DST offset; `starts_at__date` filters by local day when `USE_TZ = True`.
- `get_or_create` with `defaults`; it calls `save()`, so seat generation still runs.
- Pure functions (`plan_day`, `round_up`, `price_for`) are easy to test without a database.
- A class-level `queryset` is built once at import time; per-request filters such as `timezone.now()` belong in `get_queryset()`. A filter across a reverse relation joins rows, so `distinct()` removes duplicates.
- CSS: grid and flex children have `min-width: auto`, so wide content stretches them; `minmax(0, 1fr)` columns and `min-w-0` let `overflow-x-auto` actually scroll. `@utility` defines a custom Tailwind v4 class; `scrollbar-width` and `scrollbar-color` are the standard scrollbar properties.

---

## 2.11 Home page redesign

**Built**
- `HeroCarousel` (Client Component): the three most recent releases, with the TMDB backdrop as background, the poster, a glass card with title, tags and a "Get tickets" button. It moves on its own every 8 seconds and has dots and arrows.
- `PromoCards`: three static promotions shaped like cinema tickets (coloured stub with the v1 image, dashed tear line with notches), right below the hero. A swipeable row on mobile, three columns on desktop.
- `MovieCard` as a horizontal card: poster, title, rating, runtime, genres and today's showtimes as links (up to four, then "+N more").
- `SectionHeading`: section title with the glowing yellow bar from v1.
- The movie list API now also returns `backdrop_path` and `release_date`; the frontend has `getShowtimesOn(date)`.

**Key decisions**
- Carousel as a Client Component (state and a timer) instead of a CSS-only scroll-snap row, so it can move on its own and show dots.
- The carousel pauses on hover and focus, does not move on its own when the system asks for reduced motion, and marks hidden slides as `inert`.
- "New release" means released less than 14 days ago in Vancouver time. It is computed on the server and passed to the carousel, so the server and the browser cannot disagree near midnight.
- Promotions go right below the hero so they are visible, and are hard-coded: the cinema is fictional and there is nothing to manage yet.
- Today's showtimes for every movie come from one request (`/api/showtimes/?date=`), fetched in parallel with the movies and grouped by movie on the server, instead of one request per movie.
- The movie card is not one big link, because the time chips are links and links cannot be nested.

**Concepts**
- `"use client"` marks the boundary where components start running in the browser; props passed into it must be serializable.
- `useState` keeps a value between renders; `useEffect` runs after rendering and its cleanup function cancels the timer.
- `Promise.all` runs independent requests at the same time.
- Stacking slides in one grid cell (`col-start-1 row-start-1`) makes the container as tall as the tallest slide, without fixed heights.
- Static image imports (`import combo from "@/assets/promos/combo.png"`) give `next/image` the width and height automatically.
- Tailwind only generates classes it finds written out in full in the source, so dynamic class names must be complete strings.
- CSS scroll snap (`snap-x`, `snap-start`) makes a horizontal row stop on each card when swiping.

---

## 3.1 Auth design

**Built**
- `docs/AUTH.md`: the authentication design (decisions, alternatives, endpoints and login flow), linked from `ARCHITECTURE.md`. No code yet.

**Key decisions**
- JWT (simplejwt) instead of Django sessions. Sessions would be simpler; JWT is the common API standard and a learning goal. Refresh token rotation with a blacklist gives a real logout.
- Tokens in httpOnly cookies, not `localStorage`, so an injected script cannot read them. `access` lives 15 minutes; `refresh` lives 7 days and is only sent to `/api/auth/`.
- The browser reaches Django through Next.js rewrites (`/api/:path*`), so the cookies are first-party on the frontend domain and Server Components can read them. Cross-origin cookies would be blocked by Safari and invisible to Next.js.
- CSRF protection in two layers: `SameSite=Lax` plus Django's CSRF token sent in an `X-CSRFToken` header, also on login and register.
- A custom `accounts.User` with email login, created now because changing the user model later is very hard. The local database is reset once.

**Concepts**
- JWT: a token signed by the server that carries the user id and an expiry; the server checks the signature without a database query.
- Access vs refresh tokens: a short-lived token for every request and a long-lived one used only to get new tokens.
- httpOnly, Secure, SameSite and Path cookie attributes.
- CSRF: the browser attaches cookies to requests started by other sites; a token that only our pages can read stops it.
- First-party vs third-party cookies, and why a same-origin proxy avoids the problem.
- Next.js redirects trailing slashes by default, which breaks `POST` to Django URLs; `skipTrailingSlashRedirect` keeps them.
