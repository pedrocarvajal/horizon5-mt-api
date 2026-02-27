# PLAN: Horizon5 MT API - Django Event Messaging Platform

## Overview

API REST built with Django + DRF that acts as an event messaging hub (NATS-like pattern).
Users authenticate via JWT, belong to one or more Accounts, and push/consume events
scoped to those accounts. Events follow a key/payload model with processing state tracking.

---

## 1. Project Structure

Replace current C++ skeleton with a Django REST Framework project:

```
horizon5-mt-api/
|-- config/                              # Django project configuration
|   |-- __init__.py
|   |-- settings/
|   |   |-- __init__.py
|   |   |-- base.py                      # Shared settings (apps, middleware, DRF, JWT)
|   |   |-- local.py                     # DEBUG=True, local postgres
|   |   |-- production.py               # DEBUG=False, gunicorn, security headers
|   |   |-- test.py                      # Fast hasher, in-memory cache
|   |-- urls.py                          # Root URL router
|   |-- wsgi.py
|   |-- asgi.py
|-- app/                                 # Single Django app (Laravel-style layout)
|   |-- __init__.py
|   |-- apps.py                          # AppConfig for "app"
|   |-- http/
|   |   |-- __init__.py
|   |   |-- controllers/                 # Views organized as controllers
|   |   |   |-- __init__.py
|   |   |   |-- health.py     # GET /health -> 200 {"status": "ok"}
|   |   |   |-- auth.py       # login, refresh, logout, me
|   |   |   |-- account.py    # CRUD accounts, members
|   |   |   |-- event.py      # push, consume, acknowledge, history
|   |   |-- requests/                    # Input serializers (like FormRequests)
|   |   |   |-- __init__.py
|   |   |   |-- auth/
|   |   |   |   |-- __init__.py
|   |   |   |   |-- login.py
|   |   |   |   |-- refresh.py
|   |   |   |-- account/
|   |   |   |   |-- __init__.py
|   |   |   |   |-- create_account.py
|   |   |   |   |-- add_member.py
|   |   |   |-- event/
|   |   |       |-- __init__.py
|   |   |       |-- push_event.py
|   |   |-- resources/                   # Output serializers (like API Resources)
|   |   |   |-- __init__.py
|   |   |   |-- user.py
|   |   |   |-- account.py
|   |   |   |-- event.py
|   |   |-- middleware/
|   |   |   |-- __init__.py
|   |   |   |-- throttling.py            # RoleBasedThrottle (rate limit by user role)
|   |   |-- permissions/                 # DRF permission classes (like Policies)
|   |       |-- __init__.py
|   |       |-- role.py                  # IsRoot
|   |       |-- account.py              # IsAccountMember, IsAccountOwner
|   |       |-- event.py                # CanPushEvents, CanConsumeEvents
|   |-- models/                          # Django ORM models (PostgreSQL)
|   |   |-- __init__.py                  # Imports all models for Django ORM discovery
|   |   |-- base.py                      # TimestampedModel (abstract)
|   |   |-- user.py                      # CustomUser
|   |   |-- account.py                   # Account, UserAccount
|   |-- documents/                       # MongoDB documents (pymongo)
|   |   |-- __init__.py
|   |   |-- event.py                     # Event document schema + queries
|   |-- database/
|   |   |-- __init__.py
|   |   |-- mongodb.py                   # MongoDB connection (pymongo client singleton)
|   |-- enums/
|   |   |-- __init__.py
|   |   |-- system_role.py              # SystemRole: root, platform, producer
|   |   |-- account_role.py             # AccountRole: owner, platform, producer
|   |   |-- event_status.py             # EventStatus: pending, delivered, processed, failed
|   |-- exceptions/
|   |   |-- __init__.py
|   |-- admin/
|   |   |-- __init__.py                  # Register all models for Django admin
|   |-- management/
|   |   |-- __init__.py
|   |   |-- commands/
|   |       |-- __init__.py
|   |       |-- check_stuck_events.py   # Check for stuck delivered events
|   |       |-- clean_expired_media.py  # Clean up expired media files
|   |       |-- get_producer_credentials.py  # Get producer credentials
|   |       |-- purge_account_snapshots.py   # Purge old account snapshots
|   |       |-- purge_events.py         # Purge terminal events
|   |       |-- purge_heartbeats.py     # Purge old heartbeats
|   |       |-- purge_logs.py           # Purge old logs
|   |       |-- purge_strategy_snapshots.py  # Purge old strategy snapshots
|   |       |-- seed_database.py        # Seed database with initial data
|   |-- monitors/                        # Individual monitor checks
|   |   |-- __init__.py
|   |   |-- stuck_events.py
|   |   |-- failed_events.py
|   |   |-- pending_backlog.py
|   |-- migrations/
|-- scripts/
|   |-- make/                            # Shell scripts invoked by Makefile
|   |   |-- run-dev.sh                   # Start dev environment
|   |   |-- run-docker-up.sh             # docker compose up
|   |   |-- run-docker-build.sh          # docker compose build
|   |   |-- run-docker-down.sh           # docker compose down
|   |   |-- run-db-migrate.sh            # Run Django migrations
|   |   |-- run-db-seed-database.sh      # Create superuser / seed data
|   |   |-- run-tests.sh                 # Run test suite
|   |   |-- run-linter-checks.sh         # ruff format --check + ruff check + pyright
|   |   |-- run-linter-fixes.sh          # ruff format + ruff check --fix
|   |   |-- run-hooks-install.sh         # Configure git hooks path
|   |-- helpers/
|       |-- logger.sh                    # Shared logger (colors, timestamps, log-to-file)
|-- .githooks/
|   |-- pre-commit                       # run-linter-fixes + run-linter-checks on staged files
|   |-- pre-push                         # run-tests on testable code changes
|-- requirements/
|   |-- base.txt
|   |-- local.txt
|   |-- production.txt
|-- Makefile                             # Entry point: each target delegates to scripts/make/
|-- pyproject.toml                       # Ruff, pyright, project metadata
|-- Dockerfile
|-- docker-compose.yml
|-- .dockerignore
|-- crontab                              # Supercronic schedule file
|-- manage.py
|-- .env.example
|-- .gitignore
```

### 1.1 Decisions

- **Single Django app (`app/`)**: Laravel-style flat structure grouped by concern type, not by domain
- **Settings split**: `base.py`, `local.py`, `production.py`, `test.py` using `django-environ`
- **Controllers**: DRF APIViews in `http/controllers/`, one file per resource (like Laravel controllers)
- **Requests**: Input validation serializers in `http/requests/`, grouped by domain (like FormRequests)
- **Resources**: Output serializers in `http/resources/`, one file per model (like API Resources)
- **Permissions**: DRF permission classes in `http/permissions/` (like Laravel Policies)
- **Models split**: One file per model in `models/`, `__init__.py` re-exports them all for Django ORM
- **Enums**: Python enums in `enums/`, one file per enum group (like Laravel Enums)

---

## 2. Docker Setup

### 2.1 Dockerfile (multi-stage)

- **Builder stage**: `python:3.12-slim`, install pip wheels from `requirements/production.txt`
- **Production stage**: `python:3.12-slim`, non-root `django` user, copy wheels, collectstatic
- **CMD**: `gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4`

### 2.2 Docker Compose Services

| Service                   | Image         | Purpose                                           |
| ------------------------- | ------------- | ------------------------------------------------- |
| `horizon-mt-api-postgres` | `postgres:16` | User/Account data, health check (pg_isready)      |
| `horizon-mt-api-mongodb`  | `mongo:7`     | Event store, health check (mongosh)               |
| `horizon-mt-api-migrate`  | build context | One-shot: `python manage.py migrate`              |
| `horizon-mt-api-web`      | build context | Gunicorn, depends on migrate + postgres + mongodb |
| `horizon-mt-api-cron`     | build context | Supercronic, scheduled monitors + tasks           |

### 2.3 Key Details

- Postgres health check: `pg_isready -U $POSTGRES_USER -d $POSTGRES_DB`
- MongoDB health check: `mongosh --eval "db.adminCommand('ping')"`
- `migrate` service runs with `condition: service_healthy` on postgres
- `web` service depends on postgres (healthy) + mongodb (healthy) + migrate (completed)
- Volumes: `postgres_data` for PostgreSQL, `mongodb_data` for MongoDB
- `.dockerignore`: exclude `.git`, `.env`, `__pycache__`, `*.pyc`, `.vscode`
- **Networks**: Explicit `backend` bridge network for all services. Database ports bound to `127.0.0.1` only in development, not exposed in production
- **MongoDB authentication**: Enabled via `MONGO_INITDB_ROOT_USERNAME` / `MONGO_INITDB_ROOT_PASSWORD` environment variables. Connection URI includes credentials

### 2.4 Environment Variables

All configuration via environment variables. Development uses `.env` file, production uses host environment or Docker env.

| Variable                     | Description                             |
| ---------------------------- | --------------------------------------- |
| `DJANGO_SECRET_KEY`          | Django secret key (also used for JWT)   |
| `DJANGO_SETTINGS_MODULE`     | Settings module path                    |
| `DATABASE_URL`               | PostgreSQL connection string            |
| `MONGODB_URI`                | MongoDB connection string               |
| `MONGO_INITDB_ROOT_USERNAME` | MongoDB root user                       |
| `MONGO_INITDB_ROOT_PASSWORD` | MongoDB root password                   |
| `POSTGRES_USER`              | PostgreSQL user                         |
| `POSTGRES_PASSWORD`          | PostgreSQL password                     |
| `POSTGRES_DB`                | PostgreSQL database name                |
| `CORS_ALLOWED_ORIGINS`       | Comma-separated allowed origins for API |

- `.env.example` provides a template with all required variables
- `.gitignore` includes `.env`
- Never commit secrets to the repository

---

## 3. Makefile & Scripts

Same pattern as enaria-middleware: the `Makefile` is a thin dispatcher, each target delegates
to a shell script in `scripts/make/`. All scripts source `scripts/helpers/logger.sh` for
consistent colored output and log-to-file support.

### 3.1 Makefile Targets

| Target                 | Script                    | Description                                  |
| ---------------------- | ------------------------- | -------------------------------------------- |
| `run-dev`              | `run-dev.sh`              | Build + up + migrate + runserver (local dev) |
| `run-docker-up`        | `run-docker-up.sh`        | `docker compose up -d`                       |
| `run-docker-build`     | `run-docker-build.sh`     | `docker compose build`                       |
| `run-docker-down`      | `run-docker-down.sh`      | `docker compose down --remove-orphans`       |
| `run-db-migrate`       | `run-db-migrate.sh`       | `python manage.py migrate` inside container  |
| `run-db-seed-database` | `run-db-seed-database.sh` | Create superuser / seed initial data         |
| `run-tests`            | `run-tests.sh`            | Run pytest inside container                  |
| `run-linter-checks`    | `run-linter-checks.sh`    | ruff format --check + ruff check + pyright   |
| `run-linter-fixes`     | `run-linter-fixes.sh`     | ruff format + ruff check --fix               |
| `run-hooks-install`    | `run-hooks-install.sh`    | Set git hooks path to `.githooks/`           |

### 3.2 Script Pattern

Each script follows the same structure:

```bash
#!/bin/bash
set -e

source "$(dirname "$0")/../helpers/logger.sh"
log_setup "<script-name>"

log_title "DESCRIPTION"
log_info "Doing something..."
# actual commands here
log_info "Done"
```

### 3.3 Logger Helper (`scripts/helpers/logger.sh`)

Shared shell functions with colored output and file logging:

| Function      | Color  | Purpose                    |
| ------------- | ------ | -------------------------- |
| `log_setup`   | -      | Set log file name in logs/ |
| `log_title`   | -      | Section header with banner |
| `log_info`    | Green  | Normal progress messages   |
| `log_warning` | Yellow | Non-critical warnings      |
| `log_error`   | Red    | Error messages             |
| `log_debug`   | Cyan   | Verbose debug output       |

### 3.4 Linting & Formatting (`pyproject.toml`)

All tool config lives in `pyproject.toml`. Same stack as horizon5-connect:

**Ruff** (linter + formatter):

```toml
[tool.ruff]
line-length = 120
target-version = "py312"

[tool.ruff.lint]
select = [
    "E",      # pycodestyle errors
    "W",      # pycodestyle warnings
    "F",      # pyflakes
    "I",      # isort
    "N",      # pep8-naming
    "UP",     # pyupgrade
    "B",      # flake8-bugbear
    "C4",     # flake8-comprehensions
    "DTZ",    # flake8-datetimez
    "T20",    # flake8-print
    "RET",    # flake8-return
    "SIM",    # flake8-simplify
    "ARG",    # flake8-unused-arguments
    "PTH",    # flake8-use-pathlib
    "PL",     # pylint
    "RUF",    # ruff-specific rules
    "S",      # flake8-bandit (security: eval, exec, hardcoded passwords, etc.)
]
ignore = [
    "UP045",   # Optional[X] vs X | None
    "UP006",   # list vs List
    "UP035",   # typing.List/Dict deprecated
    "UP007",   # Union[X, Y] vs X | Y
    "PLR0913", # Too many arguments
]

[tool.ruff.lint.per-file-ignores]
"app/migrations/*" = ["ALL"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

**Pyright** (type checker):

```toml
[tool.pyright]
pythonVersion = "3.12"
typeCheckingMode = "basic"
include = ["app", "config"]
exclude = [".venv", "__pycache__", "app/migrations"]
```

### 3.5 Linter Scripts

**`run-linter-checks.sh`** - Runs all checks without modifying files:

1. `ruff format --check` (verify formatting)
2. `ruff check` (lint rules)
3. `pyright` (type checking)

Supports `--file` and `--folder` flags for targeted checks.

**`run-linter-fixes.sh`** - Auto-fixes what it can:

1. `ruff format .` (apply formatting)
2. `ruff check --fix .` (auto-fix lint issues)

### 3.6 Git Hooks (`.githooks/`)

Custom hooks directory, activated via `git config core.hooksPath .githooks`.
Installed with `make run-hooks-install`.

**pre-commit**:

1. Get staged Python files (`git diff --cached --name-only --diff-filter=ACM | grep '\.py$'`)
2. Run `ruff format` + `ruff check --fix` on staged files only
3. Re-stage formatted files (`git add`)
4. Run `make run-linter-checks` - abort commit if it fails

**pre-push**:

1. Detect changed files between local and remote
2. Check if changes touch testable paths (`app/http/`, `app/models/`, `app/enums/`, etc.)
3. If testable changes found: run `make run-tests` - abort push if tests fail
4. If only non-testable changes (docs, scripts, config): skip tests

---

## 4. Requirements

### 4.1 base.txt

```
django>=5.2,<5.3
djangorestframework>=3.16
djangorestframework-simplejwt>=5.5
django-environ>=0.12
django-cors-headers>=4.7
pymongo>=4.15
structlog>=24.0.0
```

### 4.2 local.txt

```
-r base.txt
ruff>=0.14.0
pyright>=1.1.390
pytest>=8.0
pytest-django>=4.10
```

### 4.3 production.txt

```
-r base.txt
gunicorn>=23.0
```

---

## 5. Database Models

### 5.1 Core - TimestampedModel (abstract)

| Field        | Type     | Notes             |
| ------------ | -------- | ----------------- |
| `created_at` | DateTime | auto_now_add=True |
| `updated_at` | DateTime | auto_now=True     |

### 5.2 Users - CustomUser

| Field        | Type         | Notes                                              |
| ------------ | ------------ | -------------------------------------------------- |
| `id`         | UUID         | Primary key, auto-generated                        |
| `email`      | EmailField   | Unique, used as USERNAME_FIELD                     |
| `password`   | CharField    | Managed by Django's auth system                    |
| `role`       | CharField    | SystemRole choices: `root`, `platform`, `producer` |
| `is_active`  | BooleanField | Default True                                       |
| `deleted_at` | DateTime     | Nullable, soft-delete timestamp                    |

- Custom `UserManager` with `create_user(email, password)` and `create_superuser`
- `AUTH_USER_MODEL = "app.CustomUser"`
- No username field; login by email

### 5.3 Accounts - Account

| Field            | Type      | Notes                           |
| ---------------- | --------- | ------------------------------- |
| `id`             | UUID      | Primary key                     |
| `account_number` | CharField | Unique, indexed                 |
| `deleted_at`     | DateTime  | Nullable, soft-delete timestamp |

### 5.4 Accounts - UserAccount (M2M through model)

| Field        | Type       | Notes                                                |
| ------------ | ---------- | ---------------------------------------------------- |
| `id`         | UUID       | Primary key                                          |
| `user_id`    | ForeignKey | -> CustomUser                                        |
| `account_id` | ForeignKey | -> Account                                           |
| `role`       | CharField  | AccountRole choices: `owner`, `platform`, `producer` |

- `unique_together = ("user", "account")`
- Allows one user to have different roles in different accounts

### 5.5 Events - Event (MongoDB collection)

Stored in MongoDB, not PostgreSQL. Accessed via `pymongo` directly (not Django ORM).

| Field          | Type     | Notes                                         |
| -------------- | -------- | --------------------------------------------- |
| `_id`          | ObjectId | MongoDB auto-generated primary key            |
| `consumer_id`  | string   | Null, identifies which service consumed it    |
| `account_id`   | UUID     | Reference to Account (PostgreSQL)             |
| `user_id`      | UUID     | Reference to CustomUser, who pushed the event |
| `key`          | string   | Event type identifier (e.g. `order.created`)  |
| `payload`      | object   | Arbitrary event data                          |
| `response`     | object   | Null, optional response data set on ack       |
| `status`       | string   | `pending`, `delivered`, `processed`, `failed` |
| `delivered_at` | datetime | Null until consumed                           |
| `processed_at` | datetime | Null until marked processed                   |
| `attempts`     | int      | Default 0, retry tracking                     |
| `created_at`   | datetime | Auto-set on insert                            |
| `updated_at`   | datetime | Auto-set on update                            |

- Compound index on `{account_id, status, created_at}` for efficient consume queries
- Events are immutable once created (payload never changes)
- Status transitions: `pending` -> `delivered` -> `processed` (or `failed`)
- `account_id` and `user_id` are stored as UUID strings referencing PostgreSQL records
- `key` field validation: regex `^[a-z][a-z0-9]*(\.[a-z][a-z0-9]*)*$`, max length 255 characters
- `payload` max size: 64KB serialized JSON, max nesting depth: 5 levels (enforced in serializer)
- **NoSQL injection prevention**: All MongoDB queries go through `app/documents/event.py` abstraction layer. Input values are strictly type-cast (`UUID` for account_id/user_id, `str` for key, enum member for status) before building queries. Never pass raw request data to pymongo.
- **Referential integrity**: `Account` and `CustomUser` use soft-delete (`deleted_at` nullable datetime) instead of physical deletion to prevent orphaned events in MongoDB

---

## 6. Authentication (JWT)

### 6.1 Stack

- `djangorestframework-simplejwt` (standard, Jazzband-maintained)
- Token blacklist enabled for refresh rotation

### 6.2 Configuration

| Setting                    | Value                                   |
| -------------------------- | --------------------------------------- |
| `ACCESS_TOKEN_LIFETIME`    | 15 minutes                              |
| `REFRESH_TOKEN_LIFETIME`   | 7 days                                  |
| `ROTATE_REFRESH_TOKENS`    | True                                    |
| `BLACKLIST_AFTER_ROTATION` | True                                    |
| `ALGORITHM`                | HS256                                   |
| `SIGNING_KEY`              | Django `SECRET_KEY` (simplejwt default) |
| `AUTH_HEADER_TYPES`        | ("Bearer",)                             |

### 6.3 Auth Endpoints

| Method | Path                    | Description             | Auth Required      |
| ------ | ----------------------- | ----------------------- | ------------------ |
| POST   | `/api/v1/auth/login/`   | Obtain access + refresh | No                 |
| POST   | `/api/v1/auth/refresh/` | Refresh access token    | No (refresh token) |
| POST   | `/api/v1/auth/logout/`  | Blacklist refresh token | Yes                |

### 6.4 Brute Force Protection

- **Login throttle**: Dedicated `LoginRateThrottle` class applied only to `/api/v1/auth/login/`
- Rate: **5 requests/minute per IP** and **10 requests/hour per email**
- After 10 consecutive failed attempts for the same email: temporary account lock for 15 minutes
- All failed login attempts are logged with IP, email, and timestamp (see section 11)

---

## 7. Roles & Permissions

### 7.1 Roles

Two separate role enums to avoid privilege confusion between system-level and account-level access:

**SystemRole** (`app/enums/system_role.py`) - Used in `User.role`:

| Role       | Description                                                             |
| ---------- | ----------------------------------------------------------------------- |
| `root`     | Full control: manage users, accounts, events, consume, push, everything |
| `platform` | Event operations: consume pending events, mark as processed (ack)       |
| `producer` | Push events to accounts, consume responses from acknowledged events     |

**AccountRole** (`app/enums/account_role.py`) - Used in `UserAccount.role`:

| Role       | Description                                                            |
| ---------- | ---------------------------------------------------------------------- |
| `owner`    | Full control within the account scope                                  |
| `platform` | Event operations within the account: consume pending events, ack       |
| `producer` | Push events to the account, consume responses from acknowledged events |

Each permission class documents explicitly which role field it checks (system-level vs account-level).

### 7.2 Permission Matrix

| Action                          | `root` | `platform` | `producer` |
| ------------------------------- | ------ | ---------- | ---------- |
| Manage users                    | Yes    | No         | No         |
| Manage accounts                 | Yes    | No         | No         |
| Push events                     | Yes    | No         | Yes        |
| Consume pending events          | Yes    | Yes        | No         |
| Acknowledge events (ack)        | Yes    | Yes        | No         |
| Read event history              | Yes    | Yes        | Yes        |
| Consume responses (ack payload) | Yes    | No         | Yes        |

### 7.3 Implementation Strategy

- Custom DRF permission classes checking `user.role` or `UserAccount.role` for account-scoped operations
- No `django-guardian` needed (no per-object permission queries)
- Add `django-rules` in the future if conditional logic grows complex

### 7.4 DRF Permission Classes

| Class              | Role Scope  | Logic                                              |
| ------------------ | ----------- | -------------------------------------------------- |
| `IsRoot`           | SystemRole  | `user.role == "root"`                              |
| `IsAccountMember`  | AccountRole | User has any `UserAccount` for the target account  |
| `CanPushEvents`    | AccountRole | Account role is `owner` or `producer`              |
| `CanConsumeEvents` | AccountRole | Account role is `owner` or `platform`              |
| `CanAckEvents`     | AccountRole | Account role is `owner` or `platform`              |
| `CanReadHistory`   | AccountRole | Account role is `owner`, `platform`, or `producer` |
| `CanReadResponses` | AccountRole | Account role is `owner` or `producer`              |

---

## 8. API Endpoints

### 8.1 Health

| Method | Path                | Body | Permission | Description                                              |
| ------ | ------------------- | ---- | ---------- | -------------------------------------------------------- |
| GET    | `/health/`          | -    | None       | Minimal liveness check: returns `{"status": "ok"}` 200   |
| GET    | `/health/detailed/` | -    | IsRoot     | Detailed readiness check: postgres, mongodb connectivity |

### 8.2 Auth

| Method | Path                    | Body                | Permission           | Description             |
| ------ | ----------------------- | ------------------- | -------------------- | ----------------------- |
| POST   | `/api/v1/auth/login/`   | `{email, password}` | None                 | Obtain access + refresh |
| POST   | `/api/v1/auth/refresh/` | `{refresh}`         | None (refresh token) | Refresh access token    |
| POST   | `/api/v1/auth/logout/`  | `{refresh}`         | Authenticated        | Blacklist refresh token |
| GET    | `/api/v1/auth/me/`      | -                   | Authenticated        | Get current user info   |

### 8.3 Events

| Method | Path                                           | Body             | Permission       | Description                                                   |
| ------ | ---------------------------------------------- | ---------------- | ---------------- | ------------------------------------------------------------- |
| POST   | `/api/v1/accounts/{id}/events/`                | `{key, payload}` | CanPushEvents    | Push event to account (root, producer)                        |
| POST   | `/api/v1/accounts/{id}/events/consume/`        | -                | CanConsumeEvents | Consume pending events (root, platform)                       |
| PATCH  | `/api/v1/accounts/{id}/events/{eid}/ack/`      | `{response?}`    | CanAckEvents     | Mark as processed, optional response payload (root, platform) |
| GET    | `/api/v1/accounts/{id}/events/history/`        | -                | CanReadHistory   | List all events (root, platform, producer)                    |
| GET    | `/api/v1/accounts/{id}/events/{eid}/response/` | -                | CanReadResponses | Get response payload from acknowledged event (root, producer) |

### 8.4 URL Routing

**`config/urls.py`** (root router):

```python
urlpatterns = [
    path("health/", HealthView.as_view()),
    path("health/detailed/", DetailedHealthView.as_view()),
    path("api/v1/", include("app.urls")),
    path("admin/", admin.site.urls),
]
```

**`app/urls.py`** (app router):

```python
urlpatterns = [
    path("auth/login/", LoginView.as_view()),
    path("auth/refresh/", RefreshView.as_view()),
    path("auth/logout/", LogoutView.as_view()),
    path("auth/me/", MeView.as_view()),
    path("accounts/<uuid:id>/events/", PushEventView.as_view()),
    path("accounts/<uuid:id>/events/consume/", ConsumeEventsView.as_view()),
    path("accounts/<uuid:id>/events/history/", EventHistoryView.as_view()),
    path("accounts/<uuid:id>/events/<str:eid>/ack/", AckEventView.as_view()),
    path("accounts/<uuid:id>/events/<str:eid>/response/", EventResponseView.as_view()),
]
```

Each controller file contains multiple view classes:

| Controller  | View Classes                                                                                  |
| ----------- | --------------------------------------------------------------------------------------------- |
| `health.py` | `HealthView`, `DetailedHealthView`                                                            |
| `auth.py`   | `LoginView`, `RefreshView`, `LogoutView`, `MeView`                                            |
| `event.py`  | `PushEventView`, `ConsumeEventsView`, `AckEventView`, `EventHistoryView`, `EventResponseView` |

### 8.5 Pagination

Event listing endpoints use cursor-based pagination (efficient for MongoDB).

| Setting   | Value                                               |
| --------- | --------------------------------------------------- |
| Page size | 50 (default), configurable via `?limit=N` (max 100) |
| Strategy  | Cursor-based using `created_at` + `_id`             |
| Direction | Newest first (`created_at` descending)              |

Response format:

```json
{
    "data": [...],
    "next_cursor": "base64-encoded-cursor-string",
    "has_more": true
}
```

Applied to:

- `POST /api/v1/accounts/{id}/events/consume/` (consume pending)
- `GET /api/v1/accounts/{id}/events/history/` (history)

### 8.6 CORS

Using `django-cors-headers` middleware. Configured per environment.

| Setting                  | Development | Production                          |
| ------------------------ | ----------- | ----------------------------------- |
| `CORS_ALLOW_ALL_ORIGINS` | `True`      | `False`                             |
| `CORS_ALLOWED_ORIGINS`   | -           | From `CORS_ALLOWED_ORIGINS` env var |
| `CORS_ALLOW_CREDENTIALS` | `True`      | `True`                              |

Allowed methods: `GET`, `POST`, `PATCH`, `DELETE`, `OPTIONS`

Allowed headers: `Authorization`, `Content-Type`

---

## 9. Scheduled Commands (Cron Service)

Scheduled background processes for monitoring and data retention.
Implemented as standalone Django management commands executed by supercronic inside Docker.

### 9.1 Architecture

```
docker-compose.yml
  |
  |-- cron service (same Django image)
       |-- runs on schedule via supercronic (lightweight cron for containers)
       |-- executes individual management commands on schedule
```

**Why supercronic**: Standard cron has issues in containers (requires root, no stdout logging,
PID 1 problems). `supercronic` is a single binary, runs as non-root, logs to stdout
(visible in `docker compose logs`), and supports standard crontab syntax.

### 9.2 Docker Compose Service

| Service | Image         | Purpose                              |
| ------- | ------------- | ------------------------------------ |
| `cron`  | build context | Runs supercronic with `crontab` file |

- Same Docker image as `web`, different CMD
- CMD: `supercronic /app/crontab`
- Depends on: postgres (healthy) + mongodb (healthy)

### 9.3 Crontab File (`crontab`)

```
# Monitoring - daily at 03:00 UTC (staggered)
0 3 * * * python manage.py check_stuck_events
5 3 * * * python manage.py clean_expired_media

# Purge jobs - weekly on Sunday at 04:00 UTC (staggered)
0 4 * * 0 python manage.py purge_logs
5 4 * * 0 python manage.py purge_heartbeats
10 4 * * 0 python manage.py purge_events
15 4 * * 0 python manage.py purge_account_snapshots
20 4 * * 0 python manage.py purge_strategy_snapshots
```

Lives in project root, copied into Docker image.

### 9.4 Management Commands

**Monitoring commands** (wrap checks from `app/monitors/`):

| Command               | Description                                                | Schedule |
| --------------------- | ---------------------------------------------------------- | -------- |
| `check_stuck_events`  | Events in `delivered` status for more than 24h without ack | Daily    |
| `clean_expired_media` | Clean up expired media files from storage and database     | Daily    |

**Purge commands** (data retention via `BaseDocument.delete_where()`):

| Command                    | Collection         | Retention | Schedule       |
| -------------------------- | ------------------ | --------- | -------------- |
| `purge_logs`               | logs               | 90 days   | Weekly, Sunday |
| `purge_heartbeats`         | heartbeats         | 30 days   | Weekly, Sunday |
| `purge_events`             | events (terminal)  | 90 days   | Weekly, Sunday |
| `purge_account_snapshots`  | account_snapshots  | 180 days  | Weekly, Sunday |
| `purge_strategy_snapshots` | strategy_snapshots | 180 days  | Weekly, Sunday |

Each command logs its result via `structlog`. Warnings are visible in Docker logs
and can be captured by external monitoring (future).

### 9.5 Project Structure

```
app/
|-- management/
|   |-- __init__.py
|   |-- commands/
|       |-- __init__.py
|       |-- check_stuck_events.py       # Standalone: stuck events check
|       |-- clean_expired_media.py      # Standalone: expired media cleanup
|       |-- purge_logs.py               # Data retention: logs
|       |-- purge_heartbeats.py         # Data retention: heartbeats
|       |-- purge_events.py             # Data retention: terminal events
|       |-- purge_account_snapshots.py  # Data retention: account snapshots
|       |-- purge_strategy_snapshots.py # Data retention: strategy snapshots
|       |-- seed_database.py            # Seed initial users and accounts
|       |-- get_producer_credentials.py # Get producer credentials
|-- monitors/
|   |-- __init__.py
|   |-- stuck_events.py             # Check for stuck delivered events
|   |-- expired_media.py            # Check/clean expired media files
crontab                              # Crontab file for supercronic
```

Each monitor is a simple class with a `run()` method that returns a result dict.
Management commands wrap these monitors as standalone entry points.

---

## 10. Rate Limiting

Throttling per user role using DRF's built-in throttle classes.
Different roles get different request limits.

### 10.1 Throttle Rates by Role

| Role       | Rate      | Scope    |
| ---------- | --------- | -------- |
| `root`     | No limit  | -        |
| `platform` | No limit  | -        |
| `producer` | 60/minute | Per user |

### 10.2 Implementation

Custom DRF throttle class in `app/http/middleware/throttling.py` that reads
`request.user.role` and applies the corresponding rate.

```python
REST_FRAMEWORK = {
    "DEFAULT_THROTTLE_CLASSES": [
        "app.http.middleware.throttling.RoleBasedThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "role_root": None,
        "role_platform": None,
        "role_producer": "60/minute",
    },
}
```

- Unauthenticated requests: use DRF's `AnonRateThrottle` at `50/hour`
- Throttle state stored in Django's default cache (**locmem for dev only**, Redis required for production — locmem does not share state across Gunicorn workers)
- Returns `429 Too Many Requests` with `Retry-After` header when exceeded
- Request body size limit: `DATA_UPLOAD_MAX_MEMORY_SIZE = 262144` (256KB)

---

## 11. Security Audit Logging

Structured JSON logging via `structlog` for security-relevant events. All logs go to stdout for Docker log aggregation.

### 11.1 Events Logged

| Event               | Severity | Data Captured                           |
| ------------------- | -------- | --------------------------------------- |
| `login_success`     | INFO     | user_id, ip                             |
| `login_failed`      | WARNING  | email, ip, reason                       |
| `account_locked`    | WARNING  | email, ip, failed_attempts              |
| `token_blacklisted` | INFO     | user_id                                 |
| `role_changed`      | WARNING  | user_id, old_role, new_role, changed_by |
| `account_created`   | INFO     | account_id, created_by                  |
| `account_deleted`   | WARNING  | account_id, deleted_by                  |
| `permission_denied` | WARNING  | user_id, ip, path, method               |

### 11.2 Dependencies

Included in `requirements/base.txt` (see section 4.1).

---

## 12. Future Considerations (Not in Scope)

- Retry mechanism for failed/stale delivered events
