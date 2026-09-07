#!/usr/bin/env bash
set -euo pipefail

# Usage: PROJECT_ID=your-project ./scripts/create_secrets_if_missing.sh
PROJECT_ID=${PROJECT_ID:-project-fea2b537-19e5-499b-ba0}
ENV_FILE="${ENV_FILE:-.env}"
KEY_FILE="${KEY_FILE:-secrets/qr-backend-signer.json}"

# Secrets to create (will skip if not present in .env)
SECRETS="DB_USER DB_PASSWORD DB_HOST DB_PORT DB_NAME SECRET_KEY ALGORITHM ACCESS_TOKEN_EXPIRE_MINUTES \
GCP_PROJECT_ID GCP_BUCKET_NAME BACKEND_PUBLIC_URL"

get_env() {
  key="$1"
  if [ ! -f "$ENV_FILE" ]; then
    echo ""
    return
  fi
  val=$(grep -m1 -E "^${key}=" "$ENV_FILE" || true)
  if [ -z "$val" ]; then
    echo ""
    return
  fi
  val=${val#${key}=}
  # strip surrounding quotes (handle both "..." and '...')
  # remove surrounding double-quotes
  if [ "${#val}" -ge 2 ] && [ "${val:0:1}" = '"' ] && [ "${val: -1}" = '"' ]; then
    val="${val:1:${#val}-2}"
  fi
  # remove surrounding single-quotes
  if [ "${#val}" -ge 2 ] && [ "${val:0:1}" = "'" ] && [ "${val: -1}" = "'" ]; then
    val="${val:1:${#val}-2}"
  fi
  printf '%s' "$val"
}

for name in $SECRETS; do
  value=$(get_env "$name")
  if [ -z "$value" ]; then
    echo "[SKIP] $name not found in $ENV_FILE"
    continue
  fi

  if gcloud secrets describe "$name" --project="$PROJECT_ID" >/dev/null 2>&1; then
    current_value=$(gcloud secrets versions access latest --secret "$name" --project="$PROJECT_ID" 2>/dev/null || true)
    if [ -z "$current_value" ] && [ -n "$value" ]; then
      echo "[UPDATE] $name has no accessible latest value — adding new version"
      printf '%s' "$value" | gcloud secrets versions add "$name" --data-file=- --project="$PROJECT_ID"
    elif [ "$current_value" = "$value" ]; then
      echo "[OK] $name already up to date"
    else
      echo "[UPDATE] $name differs — adding new version"
      printf '%s' "$value" | gcloud secrets versions add "$name" --data-file=- --project="$PROJECT_ID"
    fi
  else
    echo "[CREATE] Creating secret: $name"
    printf '%s' "$value" | gcloud secrets create "$name" --data-file=- --replication-policy="automatic" --project="$PROJECT_ID"
  fi
done


# La clave de la cuenta de servicio de GCP es un archivo, no una línea del .env,
# así que se sube como un secreto aparte.
if [ -f "$KEY_FILE" ]; then
  name="GCP_SERVICE_ACCOUNT_KEY"
  if gcloud secrets describe "$name" --project="$PROJECT_ID" >/dev/null 2>&1; then
    echo "[UPDATE] $name — adding new version from $KEY_FILE"
    gcloud secrets versions add "$name" --data-file="$KEY_FILE" --project="$PROJECT_ID"
  else
    echo "[CREATE] Creating secret: $name from $KEY_FILE"
    gcloud secrets create "$name" --data-file="$KEY_FILE" --replication-policy="automatic" --project="$PROJECT_ID"
  fi
else
  echo "[SKIP] $KEY_FILE not found — skipping GCP_SERVICE_ACCOUNT_KEY"
fi

echo "Done. Review created secrets with: gcloud secrets list --project=$PROJECT_ID"
