#!/bin/bash
# ─────────────────────────────────────────────────────────────
#  sifusherif — SQLite backup script
#
#  Dumps the SQLite DB, compresses it, and emails it via Resend
#  SMTP relay (smtp.resend.com:587).
#
#  Environment variables required:
#    DB_PATH          — path to db.sqlite3 (default: /app/data/db.sqlite3)
#    BACKUP_EMAIL_TO  — recipient address (your personal email)
#    RESEND_API_KEY   — your Resend API key (used as SMTP password)
#    DEFAULT_FROM_EMAIL — sender address (must be a verified Resend domain)
# ─────────────────────────────────────────────────────────────

set -euo pipefail

DB_PATH="${DB_PATH:-/app/data/db.sqlite3}"
BACKUP_DIR="/tmp/db_backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/sifusherif_${TIMESTAMP}.sqlite3"
ARCHIVE_FILE="${BACKUP_FILE}.gz"

FROM_EMAIL="${DEFAULT_FROM_EMAIL:-backups@sifusherif.dev}"
TO_EMAIL="${BACKUP_EMAIL_TO}"
RESEND_KEY="${RESEND_API_KEY}"

# ── 1. Sanity checks ─────────────────────────────────────────
if [[ -z "${TO_EMAIL}" ]]; then
  echo "[backup] ERROR: BACKUP_EMAIL_TO is not set." >&2
  exit 1
fi

if [[ -z "${RESEND_KEY}" ]]; then
  echo "[backup] ERROR: RESEND_API_KEY is not set." >&2
  exit 1
fi

if [[ ! -f "${DB_PATH}" ]]; then
  echo "[backup] ERROR: DB file not found at ${DB_PATH}" >&2
  exit 1
fi

# ── 2. Create a hot backup using the sqlite3 CLI (.backup) ───
mkdir -p "${BACKUP_DIR}"
echo "[backup] Starting SQLite hot backup..."
sqlite3 "${DB_PATH}" ".backup '${BACKUP_FILE}'"
echo "[backup] Backup written to ${BACKUP_FILE}"

# ── 3. Compress ──────────────────────────────────────────────
gzip -9 "${BACKUP_FILE}"
ARCHIVE_SIZE=$(du -sh "${ARCHIVE_FILE}" | cut -f1)
echo "[backup] Compressed to ${ARCHIVE_FILE} (${ARCHIVE_SIZE})"

# ── 4. Base64-encode for email attachment ────────────────────
ATTACHMENT_B64=$(base64 -w 0 "${ARCHIVE_FILE}")
ATTACHMENT_NAME="sifusherif_${TIMESTAMP}.sqlite3.gz"

# ── 5. Send via Resend API (HTTP) ────────────────────────────
echo "[backup] Sending backup to ${TO_EMAIL} via Resend..."

HTTP_STATUS=$(curl -s -o /tmp/resend_response.json -w "%{http_code}" \
  --request POST \
  --url 'https://api.resend.com/emails' \
  --header "Authorization: Bearer ${RESEND_KEY}" \
  --header 'Content-Type: application/json' \
  --data "{
    \"from\": \"${FROM_EMAIL}\",
    \"to\": [\"${TO_EMAIL}\"],
    \"subject\": \"[sifusherif] DB Backup — ${TIMESTAMP}\",
    \"html\": \"<p>Automated SQLite database backup for <strong>sifusherif.dev</strong>.</p><p>Timestamp: <code>${TIMESTAMP}</code><br>Size: <strong>${ARCHIVE_SIZE}</strong></p><p>The backup file is attached.</p>\",
    \"attachments\": [
      {
        \"filename\": \"${ATTACHMENT_NAME}\",
        \"content\": \"${ATTACHMENT_B64}\"
      }
    ]
  }")

if [[ "${HTTP_STATUS}" == "200" ]]; then
  echo "[backup] ✓ Email sent successfully."
else
  echo "[backup] ERROR: Resend API returned HTTP ${HTTP_STATUS}" >&2
  cat /tmp/resend_response.json >&2
  exit 1
fi

# ── 6. Cleanup ───────────────────────────────────────────────
rm -f "${ARCHIVE_FILE}" /tmp/resend_response.json
echo "[backup] Done. Cleanup complete."
