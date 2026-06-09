from .base import *  # noqa
from decouple import config

DEBUG = False

import os

# In production (Docker) the DB lives on a named volume at /app/data/
# so it survives container rebuilds. DB_PATH takes precedence; DB_NAME
# is the legacy fallback for non-Docker deployments.
_db_path = config('DB_PATH', default='')
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': _db_path if _db_path else BASE_DIR / config('DB_NAME', default='db.sqlite3'),
    }
}

# ── Caching: Redis ────────────────────────────────────────────────────────────
# django-redis gives us: full cache API, cache invalidation, and connection pooling.
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            'IGNORE_EXCEPTIONS': True,   # degrade gracefully if Redis is down
        },
        'KEY_PREFIX': 'sifusherif',
        'TIMEOUT': 600,   # 10 min default; overridden per-view with cache_page()
    }
}

SESSION_ENGINE   = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# ── Security ──────────────────────────────────────────────────────────────────
SECURE_HSTS_SECONDS        = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD        = True
SECURE_SSL_REDIRECT         = True
SESSION_COOKIE_SECURE       = True
CSRF_COOKIE_SECURE          = True
SECURE_BROWSER_XSS_FILTER  = True
SECURE_CONTENT_TYPE_NOSNIFF= True
X_FRAME_OPTIONS             = 'DENY'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ── Email: Resend (SMTP relay) ────────────────────────────────────────────────
# Resend works as a drop-in SMTP relay — no extra package required.
# Add RESEND_API_KEY to your .env when you set up Resend.
# Docs: https://resend.com/docs/send-with-smtp
EMAIL_BACKEND       = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST          = 'smtp.resend.com'
EMAIL_PORT          = 587
EMAIL_USE_TLS       = True
EMAIL_HOST_USER     = 'resend'                          # always the literal string "resend"
EMAIL_HOST_PASSWORD = config('RESEND_API_KEY', default='')
DEFAULT_FROM_EMAIL  = config('DEFAULT_FROM_EMAIL', default='sherif@sifusherif.dev')
