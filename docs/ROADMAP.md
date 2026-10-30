# Roadmap

Each phase ends with something that works and can be shown. Each step is meant to be one focused working session: plan it, build it, test it, understand it, commit it.

Legend: `[x]` done, `[ ]` pending.

---

## Phase 1: Foundation

Goal: both apps run locally against Postgres and Redis, and CI checks every push.

- [x] **1.1 Monorepo scaffold.** `backend/` (Django project with `config/` and empty apps), `frontend/` (Next.js config files), `docker-compose.yml`, `.gitignore`, README.
- [x] **1.2 Backend runs.** Virtual environment, dependencies installed, `.env` from `.env.example`, `migrate` against Postgres in Docker, admin and Swagger reachable.
- [x] **1.3 Frontend runs.** `npm install` (creates `package-lock.json`, which must be committed), `npm run dev`, home page renders with Tailwind styles. Learn: App Router file conventions, `layout.tsx` vs `page.tsx`, how Tailwind v4 reads the `@theme` block.
  - Suggested commit: `chore(frontend): install dependencies and add lockfile`
- [x] **1.4 Health check endpoint.** `GET /api/health/` returns `{"status": "ok"}` after running `SELECT 1` on the database. First pytest test for it. Learn: DRF function-based views, pytest-django fixtures (`client`, `django_db`).
  - Suggested commit: `feat(backend): add health check endpoint`
- [x] **1.5 Frontend talks to the API.** The home page (a Server Component) fetches `/api/health/` and shows the API status. Learn: Server Components, `fetch` on the server, environment variables in Next.js (`NEXT_PUBLIC_*`).
  - Suggested commit: `feat(frontend): show API status on the home page`
- [x] **1.6 Continuous integration.** GitHub Actions workflow with two jobs: backend (ruff check, ruff format --check, `makemigrations --check`, pytest with a Postgres service) and frontend (`npm ci`, lint, build). Learn: workflow syntax, service containers, caching.
  - Suggested commit: `ci: run lint, tests and build on every push`

**Done when:** `docker compose up -d`, the API and the frontend run with the README steps, and CI is green on GitHub.

---

## Phase 2: Movie listing

Goal: staff can import movies from TMDB and schedule showtimes; visitors see the listing and movie pages.

- [x] **2.1 Visual identity.** Port the v1 colors and fonts into Tailwind `@theme` tokens; base layout with header and footer.
  - Suggested commit: `feat(frontend): add v1 visual identity and base layout`
- [x] **2.2 Movie model.** `Movie` model, migration, admin registration. Tests for model basics.
  - Suggested commit: `feat(movies): add movie and genre models with admin and tests`
- [x] **2.3 TMDB client.** A small service module that fetches a movie by TMDB id (API key from `.env`). Tests mock the HTTP calls.
  - Suggested commit: `feat(movies): add tmdb client to fetch movie details`
- [x] **2.4 Import from TMDB.** Admin action or management command that imports/updates movies from TMDB.
  - Suggested commit: `feat(movies): add import_movies command to import movies from tmdb`
- [x] **2.5 Auditoriums and seats.** `Auditorium` and `Seat` models; generating seats from rows × columns; seat types.
  - Suggested commit: `feat(cinemas): add auditorium and seat models with seat generation`
- [x] **2.6 Showtimes.** `Showtime` model with overlap validation in the same auditorium. Tests for the overlap rule.
  - Suggested commit: `feat(cinemas): add showtime model with overlap validation`
- [x] **2.7 Read API.** DRF serializers and viewsets: movie list, movie detail, showtimes by movie and date. Documented in Swagger. API tests.
  - Suggested commit: `feat(backend): add read api for movies and showtimes`
- [x] **2.8 Listing page.** `/` (or `/movies`) in Next.js, server-rendered from the API, with posters via `next/image`.
  - Suggested commit: `feat(frontend): add movie listing page with posters`
- [ ] **2.9 Movie page.** `/movies/[id]` with details, trailer and showtimes grouped by date. Learn: dynamic routes, `generateMetadata`.
- [ ] **2.10 Seed data.** Management command that creates auditoriums, imports a few movies and schedules showtimes for demo purposes.

**Done when:** a visitor can browse current movies and see their showtimes, all coming from Postgres.

---

## Phase 3: Accounts

Goal: users can sign up, log in and see their profile.

- [ ] **3.1 Auth design.** Decide and document: JWT (djangorestframework-simplejwt) stored in httpOnly cookies, CSRF handling, token refresh.
- [ ] **3.2 Sign up and login API.** Register, login, logout and refresh endpoints that set and clear cookies. Tests.
- [ ] **3.3 Current user API.** `GET /api/me/`. Tests for authenticated and anonymous access.
- [ ] **3.4 Auth pages.** Sign up and login forms in Next.js (Client Components), error handling, redirects.
- [ ] **3.5 Protected routes.** Profile page that requires login; header shows the logged-in user. Learn: Next.js middleware or server-side checks with cookies.

**Done when:** a user can create an account, log in, reload the page and stay logged in, and log out.

---

## Phase 4: Live seats

Goal: a seat map per showtime that updates in real time for everyone viewing it.

- [ ] **4.1 Seat map API.** Endpoint returning every seat of a showtime with its status (available, on hold, sold).
- [ ] **4.2 Seat map UI.** Interactive seat grid in Next.js; selecting and deselecting seats locally.
- [ ] **4.3 Redis seat locks.** Lock endpoint using `SET NX EX`; all-or-nothing for multiple seats; release endpoint. Tests, including the concurrent case.
- [ ] **4.4 Channels setup.** Install Channels and channels-redis, switch to an ASGI server, routing for `ws/showtimes/<id>/`.
- [ ] **4.5 Broadcast seat changes.** When seats are locked, released or sold, notify the `showtime:{id}` group. Consumer tests.
- [ ] **4.6 Live UI.** The seat map subscribes to the WebSocket and updates without reloading.

**Done when:** two browsers on the same showtime see each other's seat holds instantly, and a held seat cannot be taken by someone else.

---

## Phase 5: Payments

Goal: paying with Stripe (test mode) turns held seats into an order.

- [ ] **5.1 Order model.** `Order` with status transitions; `Ticket` model with the unique `(showtime, seat)` constraint. Tests for the constraint.
- [ ] **5.2 Checkout session.** Endpoint that validates the user's locks, computes the total on the server and creates a Stripe Checkout session with a pending order.
- [ ] **5.3 Webhook.** Verify the Stripe signature; on payment, mark the order as paid and create tickets in one transaction; broadcast "sold". Tests with signed payloads.
- [ ] **5.4 Success and cancel pages.** Next.js pages for the Stripe redirect.
- [ ] **5.5 Expiration.** Celery beat task that expires pending orders whose locks ran out and releases the seats.

**Done when:** a test card payment creates an order with tickets, and abandoned checkouts release their seats on their own.

---

## Phase 6: Tickets

Goal: users get their ticket by email and staff can validate it.

- [ ] **6.1 Signed ticket code.** Unique code per ticket, signed with `django.core.signing`, encoded in a QR image.
- [ ] **6.2 PDF ticket.** Generate a PDF with movie, showtime, seat and QR. Tests that the PDF is produced.
- [ ] **6.3 Email task.** Celery task triggered by the webhook that builds the PDF and emails it (console backend locally, real provider in production).
- [ ] **6.4 My tickets.** API and page listing the user's tickets with download links.
- [ ] **6.5 Validation page.** Staff-only page that reads a QR code (or pasted code), checks the signature and marks the ticket as used once. Tests for reused and forged codes.

**Done when:** after paying, the user receives an email with a PDF ticket, sees it in "My tickets", and staff can validate it exactly once.

---

## Phase 7: Polish and deploy

Goal: a public demo with a README that sells the project.

- [ ] **7.1 End-to-end test.** Playwright test covering the purchase flow (with Stripe test mode). Run it in CI.
- [ ] **7.2 Demo user.** Seeded demo account and documented Stripe test card.
- [ ] **7.3 Production settings.** Security settings, static files, allowed hosts, CORS, environment-specific config.
- [ ] **7.4 Deploy.** Frontend on Vercel; API, worker, Postgres and Redis on Railway or Render.
- [ ] **7.5 README.** Screenshots, architecture diagram, "what v2 fixes from v1", live demo link.

**Done when:** anyone can open the public link, log in with the demo user and buy a ticket with the test card.
