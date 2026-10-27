# Architecture

## Overview

```
Browser ──HTTP──▶ Next.js (Vercel) ──HTTP──▶ Django REST API ──▶ PostgreSQL
   │                                            │    │
   └──────────── WebSocket (Channels) ─────────┘    ├──▶ Redis (seat locks, Channels layer, Celery broker)
                                                     │
Stripe ──webhook──▶ Django ──task──▶ Celery worker ──┴──▶ PDF + QR ticket ──▶ email
```

- **Next.js** renders the movie listing and movie pages on the server (good for SEO) and handles the interactive seat map in the browser.
- **Django + DRF** owns all business rules: availability, prices, orders, payments and ticket validation.
- **PostgreSQL** is the source of truth. Constraints guarantee that a seat can never be sold twice.
- **Redis** holds short-lived data only: seat locks with an expiry, Channels messages and Celery jobs. Losing it can release a lock early but never loses a sale.
- **Celery** runs slow work (PDF generation, emails, expiring orders) outside the request/response cycle.
- **Channels** pushes seat status changes to everyone viewing the same showtime.

## Data model

| Model | Fields |
|---|---|
| **Movie** | tmdb_id, title, synopsis, runtime, classification, release_date, poster_path, backdrop_path, trailer, genres |
| **Genre** | tmdb_id, name |
| **Auditorium** | name, rows, columns |
| **Seat** | auditorium, row, number |
| **Showtime** | movie, auditorium, starts_at, ends_at, base_price |
| **TicketType** | name, price (e.g. Regular, Child, Senior) |
| **Order** | user, showtime, status (pending, paid, cancelled, expired, refunded), total, stripe_session_id, created_at |
| **Ticket** | order, showtime, seat, ticket_type, price, unique code (for the QR), used_at |

Key rules:
- Movie data comes from TMDB, but only the fields a cinema needs are stored. TMDB returns image paths (`poster_path`, `backdrop_path`), not full URLs; the full URL is built when the image is displayed. User ratings, popularity, budget and revenue are not stored.
- TMDB has no showtimes. Staff create them in the Django admin, and a `seed_showtimes` management command generates a week of showtimes for the movies now playing.
- `Showtime.ends_at` is stored, not typed by hand: `save()` computes it from `starts_at`, the movie runtime and the cleaning time.
- A `Showtime` cannot overlap another showtime in the same auditorium (model validation using `starts_at` and `ends_at`).
- `Ticket` has a unique constraint on `(showtime, seat)`: the database rejects a double sale even if everything else fails.
- `Ticket.price` stores the price actually paid, so later price changes do not alter past sales.

## Purchase flow

1. The user opens a showtime; the frontend subscribes to the WebSocket group `showtime:{id}`.
2. When the user selects seats, the API tries to lock them in Redis (`SET key value NX EX <seconds>`). If any seat is already locked, it returns an error and locks none.
3. Channels notifies every connected client that those seats are now "on hold".
4. The API creates a pending `Order` and a Stripe Checkout session.
5. Stripe calls the webhook: the order becomes "paid" and the `Ticket` rows are created inside one database transaction.
6. A Celery task generates the PDF ticket with a QR code and emails it.
7. Channels marks the seats as "sold" for everyone.
8. If a lock expires without payment, a periodic task marks the order as expired and releases the seats.

## What v2 fixes from v1

- **Security:** v1 endpoints accepted any field from the browser, so a user could mark tickets as sold or create sales without paying. In v2 all logic runs on the server and every input is validated.
- **Business logic in the frontend** (~500 lines in `dataService.js`) moves to the API.
- **Race condition:** v1 checked availability and then updated it in separate steps. v2 uses an atomic Redis lock plus a database constraint.
- **Fixed 7×13 seat layout:** v2 makes every auditorium configurable.
- **Fake payment:** v2 uses Stripe in test mode.
- **Plain-text QR:** v2 uses a unique signed code that is validated at the entrance.
- **No auth and no tests:** v2 has accounts, tests and CI.
- **MovieGlu + image proxy:** replaced by TMDB.

## Out of scope for the first version

Concessions and combos, promotions and discount codes, multiple locations, reviews and recommendations, pre-sale notifications, mobile app or PWA for scanning.
