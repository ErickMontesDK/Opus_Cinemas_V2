# Opus Cinemas

A full stack fictional movie theater: a movie listing powered by TMDB, a real-time seat map, Stripe payments in test mode, and PDF tickets with a QR code sent by email.

It is a rebuild of a school project ([v1](https://github.com/ErickMontesDK/Opus-Cinemas), vanilla JS + jQuery) as a production-style application with a real backend.

> 🚧 Work in progress. Current phase: **3, accounts**. Visitors can already browse the movies now in theaters and their showtimes.

## Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js (App Router) + TypeScript + Tailwind CSS |
| API | Django + Django REST Framework |
| Database | PostgreSQL |
| Task queue / cache | Celery + Redis |
| Real time | Django Channels (WebSockets) |
| Movie data | TMDB API |
| Payments | Stripe Checkout (test mode) |

## Structure

```
.
├── frontend/          # Next.js + TypeScript + Tailwind
├── backend/           # Django project
│   ├── config/        # settings, urls, asgi, celery
│   ├── movies/        # movies, TMDB
│   ├── cinemas/       # auditoriums, seats, showtimes
│   ├── bookings/      # orders, seat locks, Stripe, websockets
│   └── tickets/       # PDF, QR, validation
├── docs/              # architecture, auth design and roadmap
└── docker-compose.yml # Postgres and Redis
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md): overview, data model and purchase flow.
- [Authentication](docs/AUTH.md): how users log in and stay logged in.
- [Roadmap](docs/ROADMAP.md): phases and step-by-step progress.

## Running locally

Requirements: Docker, Python 3.12 and Node.js 22+.

**1. Services (Postgres and Redis)**

```bash
docker compose up -d
```

**2. API (Django)**

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
```

Movie data comes from [TMDB](https://www.themoviedb.org/). Create a free account, copy the **API Read Access Token** from [the API settings](https://www.themoviedb.org/settings/api) and set it as `TMDB_API_TOKEN` in `backend/.env`. Then load the demo listing and start the server:

```bash
python manage.py update_listing    # auditoriums, movies now in theaters and a week of showtimes
python manage.py runserver
```

`update_listing` is safe to run again: it only schedules the days that have no showtimes yet. Options: `--movies` (default 6) and `--days` (default 7). To import specific movies by TMDB id, use `python manage.py import_movies 27205 550`.

- API docs (Swagger): http://localhost:8000/api/docs/
- Admin: http://localhost:8000/admin/

**3. Frontend (Next.js)**

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

Open http://localhost:3000 to see the home page with the movie listing. Each movie has its own page with the trailer and showtimes by day.

## Quality checks

```bash
(cd backend && ruff check . && ruff format --check . && python manage.py makemigrations --check --dry-run && pytest)
(cd frontend && npm run lint && npm run build)
```

## Roadmap

1. ✅ **Foundation**: repo, Docker Compose, Django + Postgres, Next.js with Tailwind, CI.
2. ✅ **Movie listing**: models, admin, TMDB import, listing and movie detail pages.
3. **Accounts**: sign up, login (JWT in httpOnly cookies), profile. ← current
4. **Live seats**: seat map, Redis seat locks, WebSockets.
5. **Payments**: Stripe Checkout, webhook, orders and expiration.
6. **Tickets**: PDF + QR + email with Celery, "My tickets" and validation at the entrance.
7. **Polish and deploy**: e2e tests, demo user, public deploy.
