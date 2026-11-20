# Authentication design

How users sign up, log in and stay logged in. Steps 3.2 to 3.5 of the roadmap implement this design.

## Summary

- Django REST Framework authenticates with **JWT** ([djangorestframework-simplejwt](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/)).
- The tokens live in **httpOnly cookies**, never in `localStorage`, so JavaScript cannot read them.
- The browser talks to the API **through Next.js rewrites**. The cookies belong to the frontend domain, and Server Components can read them.
- Every request that changes data needs a **CSRF token**, on top of `SameSite=Lax` cookies.
- A **custom user model** logs in with email.

## Decisions

### 1. JWT instead of Django sessions

| | JWT in httpOnly cookies | Django sessions |
|---|---|---|
| State | Inside the signed token | In the `django_session` table |
| Logout | Needs a refresh token blacklist | Delete the session |
| CSRF | We enable it ourselves | Built into `SessionAuthentication` |

Sessions would be simpler for a browser-only app. JWT was chosen because it is the common standard for APIs and a learning goal of this project. Its two weak points are covered below: the blacklist gives a real logout (decision 3), and CSRF is enforced explicitly (decision 4).

### 2. Same-origin API through Next.js rewrites

In production the frontend (Vercel) and the API (Railway or Render) have different domains. If Django set the cookies on its own domain:

1. The browser would treat them as third-party cookies, which Safari and Firefox block.
2. Next.js Server Components would never receive them, so the server could not tell whether the user is logged in.

Instead, the browser only talks to the frontend origin. Next.js [rewrites](https://nextjs.org/docs/app/api-reference/config/next-config-js/rewrites) forward `/api/:path*` to Django:

```
Browser ──/api/auth/login/──▶ Next.js (rewrite) ──▶ Django
        ◀── Set-Cookie (frontend domain) ──────────┘
```

| Caller | How it reaches the API |
|---|---|
| Browser (Client Components) | Relative URLs (`/api/...`), so cookies are sent automatically |
| Server Components | Calls Django directly with a server-only `API_URL` and forwards the incoming `Cookie` header |

Alternatives considered:
- **Custom domain with subdomains** (`opuscinemas.com` and `api.opuscinemas.com`): clean, but needs a paid domain and DNS setup.
- **Cross-origin cookies** (`SameSite=None; Secure`): blocked by Safari, invisible to Next.js, and more exposed to CSRF.

Implementation notes:
- Django URLs end with a slash, and Next.js redirects `/path/` to `/path` by default. A `POST` that gets redirected loses its body, so `next.config.ts` must keep trailing slashes (`skipTrailingSlashRedirect: true`).
- `:path*` does not keep the trailing slash, so the rule spells it out on both sides: `/api/:path*/` → `${API_URL}/api/:path*/`. Without it, Django answers `301` to add the slash back.
- The frontend has a single, server-only `API_URL` variable. The rewrite and the Server Components use it; the browser only sees relative `/api/...` URLs.
- Vercel rewrites do not proxy WebSockets. The live seat map (phase 4) connects directly to Django. This is fine: viewing seats is public, and seat actions go through authenticated HTTP endpoints.
- With same-origin requests, CORS is no longer needed for the browser. The CORS settings stay until phase 7 cleans up production settings.

### 3. Tokens and cookies

| Cookie | Holds | Lifetime | Flags |
|---|---|---|---|
| `access` | Access token | 15 minutes | `HttpOnly`, `Secure` outside local development, `SameSite=Lax`, `Path=/` |
| `refresh` | Refresh token | 7 days | Same flags, also `Path=/`, so the Next.js proxy sees it on page requests (decision 5) |

simplejwt settings:

```python
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}
```

- **Rotation:** every refresh returns a new refresh token and blacklists the old one (`rest_framework_simplejwt.token_blacklist` app). A stolen refresh token stops working as soon as the real user refreshes.
- **Logout:** blacklists the refresh token and deletes both cookies.
- **Reading the token:** simplejwt reads the `Authorization` header by default. A small custom authentication class extends `JWTAuthentication` to read the `access` cookie instead, and enforces CSRF (decision 4).
- **Invalid or expired access cookie:** the request is treated as anonymous, not rejected. Public endpoints such as the movie listing keep working when the token expires, and protected endpoints still answer `401`, which tells the frontend to refresh.
- `Secure` is driven by a setting (`True` unless `DEBUG`), because local development runs on plain HTTP.

### 4. CSRF protection: `SameSite=Lax` plus Django's CSRF token

Cookies are sent automatically, so another site could try to make the browser send a request to our API ([CSRF](https://docs.djangoproject.com/en/5.2/howto/csrf/)). Two layers stop that:

1. **`SameSite=Lax`:** modern browsers do not send the cookies with `POST` requests that come from other sites.
2. **Django's CSRF token (double submit):** Django sets a `csrftoken` cookie that JavaScript can read. The frontend copies it into an `X-CSRFToken` header on every `POST`, `PUT`, `PATCH` and `DELETE`. Another site cannot read our cookies, so it cannot build that header. The custom authentication class runs the same check as DRF's `SessionAuthentication.enforce_csrf()`.

Details:
- `GET /api/auth/csrf/` (with `ensure_csrf_cookie`) gives the browser the `csrftoken` cookie before the first form is sent.
- `CSRF_TRUSTED_ORIGINS` contains the frontend origin, because Django checks the `Origin` header of proxied requests against it.
- Login and register also require the CSRF token. Otherwise an attacker could log the victim into the attacker's account (login CSRF). DRF skips CSRF when nobody is logged in, so the auth views enforce it with a small mixin.

### 5. Refreshing the access token

The `access` cookie expires with its token after 15 minutes. Without a refresh, reloading a page after that would show the user as logged out, even with 7 days left on the refresh token.

**Next.js server (step 3.5): [`proxy.ts`](https://nextjs.org/docs/app/api-reference/file-conventions/proxy)**, the Next.js 16 name for middleware. It runs before every page, because Server Components cannot write cookies:

1. If the `access` cookie is gone but `refresh` and `csrftoken` are there, the proxy calls `POST /api/auth/refresh/` on Django, forwarding the cookies with `X-CSRFToken` and the frontend `Origin` (checked against `CSRF_TRUSTED_ORIGINS`).
2. It copies the new tokens into the request cookies, so the page in the same request already sees the user, and forwards Django's `Set-Cookie` headers to the browser.
3. The `refresh` cookie uses `Path=/` for this, since with `Path=/api/auth/` the browser would not send it with page requests. It is still `HttpOnly`, `SameSite=Lax` and only goes to our own origin.

Rotation race: two requests that refresh at the same time send the same refresh token, and the second one fails because the first one already blacklisted it. To keep that rare and harmless:
- The proxy only runs on pages: not on `/api`, build files or static files, and not on `<Link>` prefetches, which run in parallel.
- When a refresh fails, the proxy does not delete the cookies. It only renders that one request as anonymous, because another request may have stored valid cookies already.

Alternative considered: refreshing only in the browser (Client Components call `/api/me/` and refresh on `401`). It is simpler and keeps the refresh cookie on `/api/auth/`, but the header would flash "Log in" before showing the user, and the server would never know who is logged in.

**Server Components:** `getCurrentUser()` in `src/lib/session.ts` (server-only) reads the `access` cookie with `cookies()` and calls `/api/me/`. React's `cache()` shares that call between the header and the page in the same request. Reading cookies makes every page render on demand (dynamic), which is expected for a site that shows the logged-in user.

**Browser:** a small wrapper around `fetch` will refresh on a `401` and retry once, when Client Components start calling protected endpoints (seat locks, phase 4). Until then, the proxy covers every page load.

## Frontend behavior

- The header shows "Log in" to visitors. Logged-in users see a circle with their initial, their first name and a discreet "Log out" text link below it. The user part sits in a `<Suspense>` boundary, so the rest of the header does not wait for the API.
- "Log in" links to `/login?next=<current URL>`. After logging in or signing up, the user goes back to that same URL (`router.replace`, so the back button does not return to the form).
- `next` only accepts paths on this site (starting with `/` but not `//` or `/\`), to prevent open redirects. Anything else falls back to `/`.
- `/login` and `/register` redirect logged-in users to `next`.
- "Log out" calls `POST /api/auth/logout/` and fully reloads the current page (`window.location.reload()`), so leaving the session is visible and no client state of the user survives.
- There is no profile page yet. A user settings page can come later if a step needs one.

### 6. Custom user model with email login

Django recommends a [custom user model when starting a project](https://docs.djangoproject.com/en/5.2/topics/auth/customizing/#using-a-custom-user-model-when-starting-a-project), because switching later, once real data exists, is very hard.

- New `accounts` app with `User(AbstractUser)`: `email` is unique and is the login field (`USERNAME_FIELD = "email"`). `AUTH_USER_MODEL = "accounts.User"`.
- The project already ran migrations with the built-in `auth.User`, so the local database is reset once and migrated from scratch. Nothing is lost: there are no real users, and `update_listing` reloads the listing.

## Endpoints

| Method | Path | Purpose | Step |
|---|---|---|---|
| `GET` | `/api/auth/csrf/` | Set the `csrftoken` cookie | 3.2 |
| `POST` | `/api/auth/register/` | Create an account and log in (sets cookies) | 3.2 |
| `POST` | `/api/auth/login/` | Check email and password and set the cookies | 3.2 |
| `POST` | `/api/auth/logout/` | Blacklist the refresh token and delete the cookies | 3.2 |
| `POST` | `/api/auth/refresh/` | Rotate the tokens using the `refresh` cookie | 3.2 |
| `GET` | `/api/me/` | Current user, or `401` | 3.3 |

Read endpoints (movies, showtimes) stay public (`AllowAny`). Endpoints that need a user use `IsAuthenticated`.

## Login flow

```
1. Browser  GET  /api/auth/csrf/          ◀── Set-Cookie: csrftoken
2. Browser  POST /api/auth/login/         (X-CSRFToken header, email + password)
            ◀── Set-Cookie: access (15 min), refresh (7 days)
3. Browser  GET  /movies/1                (page request, access cookie sent automatically)
            Next.js server  GET /api/me/  (forwards the access cookie) → header shows the user
4. ...15 minutes later, the browser drops the expired access cookie
5. Browser  GET  /movies/1                (only the refresh and csrftoken cookies)
            proxy.ts  POST /api/auth/refresh/  (refresh cookie, X-CSRFToken, Origin)
            ◀── Set-Cookie: new access, new refresh (old refresh blacklisted)
            The page renders with the new access token, and the browser stores the new cookies.
```
