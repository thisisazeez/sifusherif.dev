from .base import *  # noqa
from decouple import config

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ── Caching: in-process memory for local dev ──────────────────────────────────
# Fast, zero config. Clears on every server restart — which is fine locally.
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'sifusherif-local',
    }
}

# ── Email: print to terminal ───────────────────────────────────────────────────
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
