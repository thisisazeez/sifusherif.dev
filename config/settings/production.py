from .base import *  # noqa
from decouple import config

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / config('DB_NAME', default='db.sqlite3'),
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

# ── Email: SMTP ───────────────────────────────────────────────────────────────
EMAIL_BACKEND   = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST      = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT      = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS   = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
