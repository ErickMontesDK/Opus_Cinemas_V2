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

## Data model (first draft)

| Model | Fields |
|---|---|
| **Movie** | tmdb_id, title, synopsis, runtime, rating, poster, trailer, genres |
| **Auditorium** | name, rows, columns |
| **Seat** | auditorium, row, number, type (standard, VIP, accessible) |
| **Showtime** | movie, auditorium, starts_at, base_price, language/format |
| **Order** | user, showtime, status (pending, paid, cancelled, expired), total, stripe_session_id, created_at |
| **Ticket** | order, showtime, seat, unique code (for the QR), used_at |

Key rules:
- `Ticket` has a unique constraint on `(showtime, seat)`: the database rejects a double sale even if everything else fails.
- A `Showtime` cannot overlap another showtime in the same auditorium (model validation).

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
