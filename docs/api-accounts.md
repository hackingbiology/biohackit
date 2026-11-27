# Accounts API

Endpoints under `/api/` for registration, sign-in tokens and profiles. Source: `backend/accounts/views.py`, `backend/accounts/serializers.py`, `backend/accounts/urls.py`. Token lifetimes are in `SIMPLE_JWT` in `backend/biohackit/settings.py`: access 15 minutes, refresh 7 days. Account erasure (`/api/auth/me/erase/`) is documented in `docs/api-labs.md`.

## `POST /api/auth/register/`

Open to anyone (no credentials needed). Creates an account and its profile in one transaction.

```json
{
  "email": "required, must not belong to another account (compared ignoring case)",
  "password": "required, checked by Django's password validators",
  "display_name": "optional, a slug of at most 50 characters, must be unused; default user-<id>"
}
```

- `201` with the new account: `id`, `email`, `is_public` and `profile` (see `GET /api/auth/me/`).
- `400` with the field errors (invalid email, email in use, weak password, display name taken or not a slug). Nothing is stored.

## `POST /api/auth/token/`

Open to anyone. The simplejwt `TokenObtainPairView`: send `email` and `password`; the answer is `200` with `access` and `refresh` tokens. Wrong credentials: `401`. The access token goes in the `Authorization: Bearer ...` header of every other endpoint.

## `POST /api/auth/token/refresh/`

Open to anyone. The simplejwt `TokenRefreshView`: send `refresh`; the answer is `200` with a new `access` token. An invalid or expired refresh token: `401`. Whether a new refresh token is returned is unknown from the repository code read here (`ROTATE_REFRESH_TOKENS` is false).

## `GET /api/auth/me/`

Authenticated (JWT, or the browser session cookie). Returns the caller's account: `id`, `email`, `is_public` and `profile` with `display_name`, `date_of_birth`, `sex`, `ethnicity`, `height_cm`, `is_public` and `social_handles` (each `platform`, `handle`, `url`). Without valid credentials: `401`.

## `GET /api/profiles/<display_name>/`

Open to anyone, no credentials read. Returns the profile with the same fields as `profile` above. The profile is returned only when both the profile and its account are public; otherwise `404` (a private profile and an unknown name look the same).
