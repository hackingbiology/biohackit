# SPDX-License-Identifier: AGPL-3.0-or-later
# biohack.it — open-source biohacking platform
# Copyright (C) HackingBiology 2026 — https://biohack.it
# Full license text: https://www.gnu.org/licenses/agpl-3.0.html

from datetime import timedelta
from pathlib import Path

import environ

from biohackit.dboptions import with_trgm_threshold

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, ["localhost", "127.0.0.1"]),
    CORS_ALLOWED_ORIGINS=(list, []),
    CSRF_TRUSTED_ORIGINS=(list, []),
    NOINDEX=(bool, False),
    EMAIL_BACKEND=(str, "django.core.mail.backends.smtp.EmailBackend"),
    DATABASE_URL=(str, "postgres://biohackit:biohackit@localhost:5432/biohackit"),
)
# Read .env file if present; CI/production inject env vars directly.
environ.Env.read_env(BASE_DIR / ".env", overwrite=False)

# --- Security --------------------------------------------------------------- #
SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env("ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = env("CSRF_TRUSTED_ORIGINS")
# Staging only: ask crawlers not to index any response (see core.middleware).
NOINDEX = env("NOINDEX")
# Staging sets the console backend: no mail transport is configured there.
EMAIL_BACKEND = env("EMAIL_BACKEND")

# --- Application definition ------------------------------------------------- #
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    # third-party
    "rest_framework",
    "rest_framework_simplejwt",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.headless",
    "allauth.mfa",
    "accounts.providers.discourse_connect",
    # local apps
    "accounts",
    "core",
    "terminology",
]

MIDDLEWARE = [
    # first, so it wraps every response (WhiteNoise, redirects, 400s)
    "core.middleware.NoIndexMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "biohackit.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

WSGI_APPLICATION = "biohackit.wsgi.application"

# --- Database --------------------------------------------------------------- #
# django-timescaledb backend wraps the standard PostgreSQL backend and adds
# TimescaleDB extension management (create_hypertable etc.).
DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default="postgres://biohackit:biohackit@localhost:5432/biohackit",
    )
}
DATABASES["default"]["ENGINE"] = "timescale.db.backends.postgresql"
# Cut-off used by the indexable `<%` word-similarity operator of the LOINC search
# (terminology/search.py). pg_trgm's default 0.6 would miss a one-letter typo of a
# six-letter word ("glucse" scores 0.571), so it is lowered for every connection.
_db_options = DATABASES["default"].setdefault("OPTIONS", {})
_db_options["options"] = with_trgm_threshold(str(_db_options.get("options", "")))

# --- Auth ------------------------------------------------------------------- #
# Custom user model is added in TG2 (accounts app).  AUTH_USER_MODEL will be
# set to 'accounts.User' once that app exists.
AUTH_USER_MODEL = "accounts.User"
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# django-allauth ------------------------------------------------------------ #
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_EMAIL_VERIFICATION = "mandatory"  # required by passkey signup
ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = True
ACCOUNT_LOGIN_BY_CODE_ENABLED = True
SITE_ID = 1
FRONTEND_URL = env("FRONTEND_URL", default="http://localhost:3000")

# Headless API (/_allauth/browser/v1/...) used by the Next.js sign-in page.
HEADLESS_ONLY = False
HEADLESS_FRONTEND_URLS = {
    "account_confirm_email": FRONTEND_URL + "/account/verify-email/{key}",
    "account_reset_password": FRONTEND_URL + "/account/password/reset",
    "account_reset_password_from_key": FRONTEND_URL
    + "/account/password/reset/key/{key}",
    "account_signup": FRONTEND_URL + "/account/signup",
    "socialaccount_login_error": FRONTEND_URL + "/account/login",
}

# Passkeys
MFA_SUPPORTED_TYPES = ["totp", "recovery_codes", "webauthn"]
MFA_PASSKEY_LOGIN_ENABLED = True
MFA_PASSKEY_SIGNUP_ENABLED = True
MFA_WEBAUTHN_ALLOW_INSECURE_ORIGIN = DEBUG

# Account linking: connect a social login to an existing account only when the
# provider marks the email verified (allauth never connects unverified emails).
SOCIALACCOUNT_EMAIL_AUTHENTICATION = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True
SOCIALACCOUNT_QUERY_EMAIL = True


def _build_social_providers():
    """Only providers with credentials in the environment are configured.

    Identity-only scopes everywhere (openid/email/profile or equivalent).
    """
    out = {}

    def app(prefix, **extra):
        cid = env(f"{prefix}_CLIENT_ID", default="")
        secret = env(f"{prefix}_SECRET", default="")
        if not (cid and secret):
            return None
        return {"client_id": cid, "secret": secret, **extra}

    simple = {
        "google": ("GOOGLE", ["profile", "email"]),
        "microsoft": ("MICROSOFT", ["User.Read"]),
        "apple": ("APPLE", ["name", "email"]),
        "facebook": ("FACEBOOK", ["email"]),
        "weixin": ("WEIXIN", ["snsapi_login"]),
    }
    for pid, (prefix, scope) in simple.items():
        a = app(prefix)
        if a:
            if pid == "apple":
                a["key"] = env("APPLE_KEY_ID", default="")
                a["settings"] = {
                    "certificate_key": env("APPLE_PRIVATE_KEY", default="")
                }
            out[pid] = {"APPS": [a], "SCOPE": scope}
    forum_url = env("RAPAMYCIN_NEWS_URL", default="")
    forum_secret = env("RAPAMYCIN_NEWS_SSO_SECRET", default="")
    if forum_url and forum_secret:
        out["discourse_connect"] = {
            "APPS": [
                {
                    "client_id": "rapamycin_news",
                    "secret": forum_secret,
                    "settings": {"url": forum_url},
                }
            ]
        }
    return out


SOCIALACCOUNT_PROVIDERS = _build_social_providers()

# djangorestframework + simplejwt ------------------------------------------- #
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    # Scoped throttles only apply to views that set `throttle_scope`.
    "DEFAULT_THROTTLE_RATES": {
        "loinc_search": env("LOINC_SEARCH_THROTTLE_RATE", default="60/min"),
    },
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# --- Internationalisation --------------------------------------------------- #
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# --- Static files ----------------------------------------------------------- #
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# --- Misc ------------------------------------------------------------------- #
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
