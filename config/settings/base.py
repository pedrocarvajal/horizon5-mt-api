from datetime import timedelta
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("DJANGO_SECRET_KEY")

ALLOWED_HOSTS: list[str] = env.list("DJANGO_ALLOWED_HOSTS", default=[])  # type: ignore[arg-type]

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "app",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

_database_url: str = env("DATABASE_URL", default="")  # type: ignore[arg-type]

if not _database_url:
    _postgres_host: str = env("POSTGRES_HOST", default="127.0.0.1")  # type: ignore[arg-type]
    _postgres_port: int = env.int("POSTGRES_PORT", default=5432)  # type: ignore[arg-type]
    _database_url = (
        f"postgres://{env('POSTGRES_USER')}:{env('POSTGRES_PASSWORD')}"
        f"@{_postgres_host}:{_postgres_port}"
        f"/{env('POSTGRES_DB')}"
    )

DATABASES = {
    "default": environ.Env.db_url_config(_database_url),
}

AUTH_USER_MODEL = "app.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGE_ROOT = BASE_DIR / "storage"
STORAGE_FILE_EXPIRATION_HOURS = env.int("STORAGE_FILE_EXPIRATION_HOURS", default=24)
STORAGE_MAX_UPLOAD_SIZE = env.int("STORAGE_MAX_UPLOAD_SIZE", default=1_073_741_824)

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

_mongodb_host: str = env("MONGODB_HOST", default="127.0.0.1")  # type: ignore[arg-type]
_mongodb_port: int = env.int("MONGODB_PORT", default=27017)  # type: ignore[arg-type]
_mongodb_database: str = env("MONGODB_DB", default=env("POSTGRES_DB"))  # type: ignore[arg-type]

MONGODB_URI = (
    f"mongodb://{env('MONGO_INITDB_ROOT_USERNAME')}:{env('MONGO_INITDB_ROOT_PASSWORD')}"
    f"@{_mongodb_host}:{_mongodb_port}"
    f"/{_mongodb_database}"
    f"?authSource=admin&directConnection=true"
)

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "app.http.middleware.role_based.RoleBasedThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "role_root": None,
        "role_platform": None,
        "role_producer": "60/minute",
        "anon": "50/hour",
    },
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "EXCEPTION_HANDLER": "app.http.exceptions.base.exception_handler",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = [
    "GET",
    "POST",
    "PATCH",
    "DELETE",
    "OPTIONS",
]
CORS_ALLOW_HEADERS = [
    "authorization",
    "content-type",
]

DATA_UPLOAD_MAX_MEMORY_SIZE = 262144

import structlog  # noqa: E402

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    logger_factory=structlog.PrintLoggerFactory(),
    wrapper_class=structlog.make_filtering_bound_logger(0),
    cache_logger_on_first_use=True,
)
