from pathlib import Path
from datetime import timedelta
from decouple import config, Csv
import dj_database_url

# ----------------------------
# BASE DIRECTORY
# ----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ----------------------------
# SECURITY
# ----------------------------
SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="localhost,127.0.0.1,human-resource-management.up.railway.app",
    cast=Csv()
)

# ----------------------------
# CUSTOM USER MODEL
# ----------------------------
AUTH_USER_MODEL = "users.User"

# ----------------------------
# AUTHENTICATION BACKENDS
# ----------------------------
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

# ----------------------------
# CSRF TRUSTED ORIGINS
# ----------------------------
CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    default="http://localhost:8000,http://127.0.0.1:8000,https://human-resource-management.up.railway.app",
    cast=Csv()
)

# ----------------------------
# INSTALLED APPS
# ----------------------------
INSTALLED_APPS = [
    # Django Apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    
    # Local apps
    'users',
    'department',
    'designation',
]

# ----------------------------
# MIDDLEWARE
# ----------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ----------------------------
# ROOT URLS & WSGI
# ----------------------------
ROOT_URLCONF = "hrms.urls"
WSGI_APPLICATION = "hrms.wsgi.application"

# ----------------------------
# TEMPLATES
# ----------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ----------------------------
# DATABASE
# ----------------------------
DATABASE_URL = config("DATABASE_URL", default=None)
CONN_MAX_AGE = config("CONN_MAX_AGE", default=50, cast=int)

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=CONN_MAX_AGE,
            conn_health_checks=True
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# ----------------------------
# PASSWORD VALIDATION
# ----------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ----------------------------
# REST FRAMEWORK & JWT
# ----------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_THROTTLE_CLASSES": (
        "users.throttles.OTPThrottle",
        "users.throttles.LoginThrottle",
    ),
    "DEFAULT_THROTTLE_RATES": {
        "otp": config("OTP_THROTTLE_RATE", default="20/hour"),
        "login": config("LOGIN_THROTTLE_RATE", default="30/hour"),
        "general": config("GENERAL_THROTTLE_SAFE_RATE", default="200/hour"),
    },
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=config("ACCESS_TOKEN_EXPIRY", default=1, cast=int)),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=config("REFRESH_TOKEN_EXPIRY", default=7, cast=int)),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}

# ----------------------------
# CACHES & SESSIONS (Redis)
# ----------------------------
REDIS_URL = config("REDIS_URL", default="redis://127.0.0.1:6379/1")

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {"ssl_cert_reqs": None},
            "IGNORE_EXCEPTIONS": True,
            "decode_responses": True,
        },
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# ----------------------------
# INTERNATIONALIZATION
# ----------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# ----------------------------
# STATIC & MEDIA FILES
# ----------------------------
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"

# ----------------------------
# EMAIL SETTINGS (SendGrid)
# ----------------------------
EMAIL_BACKEND = config("EMAIL_BACKEND", default="core.email_backends.SendGridBackend")
SENDGRID_API_KEY = config("SENDGRID_API_KEY")
EMAIL_FROM = config("EMAIL_FROM")

# ----------------------------
# SECURITY SETTINGS (Production)
# ----------------------------
SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
X_FRAME_OPTIONS = "DENY"
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# ----------------------------
# DEFAULT PK FIELD
# ----------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ----------------------------
# LOGGING
# ----------------------------
import logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO"},
    },
}
