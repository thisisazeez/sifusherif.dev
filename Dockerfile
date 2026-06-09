FROM python:3.12-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libjpeg-dev \
    libpng-dev \
    libwebp-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --prefix=/install --no-cache-dir -r requirements.txt

FROM python:3.12-slim AS runtime

RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo \
    libpng16-16 \
    sqlite3 \
    msmtp \
    msmtp-mta \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local

COPY . .

RUN DJANGO_SETTINGS_MODULE=config.settings.production \
    SECRET_KEY=build-time-placeholder \
    ALLOWED_HOSTS=* \
    python manage.py collectstatic --noinput --clear

RUN mkdir -p /app/data && chown -R appuser:appuser /app/data && \
    chown -R appuser:appuser /app/staticfiles

USER appuser

EXPOSE 7000

CMD ["gunicorn", \
     "--bind", "0.0.0.0:7000", \
     "--workers", "2", \
     "--timeout", "60", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "config.wsgi:application"]
