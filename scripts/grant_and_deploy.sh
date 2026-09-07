#!/usr/bin/env bash
set -euo pipefail

# Automate: create missing secrets, grant secretAccessor to Cloud Run service account, and trigger Cloud Build
# Usage: PROJECT_ID=project-fea2b537-19e5-499b-ba0 ./scripts/grant_and_deploy.sh

PROJECT_ID=${PROJECT_ID:-project-fea2b537-19e5-499b-ba0}
SERVICE_NAME=${SERVICE_NAME:-qr-backend}
REGION=${REGION:-us-central1}

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

echo "Project: $PROJECT_ID"
echo "Service: $SERVICE_NAME (region: $REGION)"

echo "1) Creating missing secrets from .env"
"$SCRIPT_DIR/create_secrets_if_missing.sh" || { echo "create_secrets_if_missing failed"; exit 1; }

echo "2) Obtain Cloud Run service account"
SERVICE_ACCOUNT=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --format='value(spec.template.spec.serviceAccountName)' --project="$PROJECT_ID" 2>/dev/null || true)
if [ -z "$SERVICE_ACCOUNT" ]; then
  # Aún no existe el servicio: usamos la cuenta de servicio que ya firma las URLs de GCS
  # (ver app/services/gcp_storage.py) para que Cloud Run corra con los mismos permisos.
  SERVICE_ACCOUNT="qr-backend-signer@${PROJECT_ID}.iam.gserviceaccount.com"
fi
echo "Service account: $SERVICE_ACCOUNT"

SECRETS_LIST=(DB_USER DB_PASSWORD DB_HOST DB_PORT DB_NAME SECRET_KEY ALGORITHM ACCESS_TOKEN_EXPIRE_MINUTES \
GCP_PROJECT_ID GCP_BUCKET_NAME BACKEND_PUBLIC_URL GCP_SERVICE_ACCOUNT_KEY)

echo "3) Grant secretmanager.secretAccessor to service account for each secret (will skip if secret missing)"
for name in "${SECRETS_LIST[@]}"; do
  if gcloud secrets describe "$name" --project="$PROJECT_ID" >/dev/null 2>&1; then
    echo "Granting access to $name"
    gcloud secrets add-iam-policy-binding "$name" \
      --member="serviceAccount:${SERVICE_ACCOUNT}" \
      --role="roles/secretmanager.secretAccessor" \
      --project="$PROJECT_ID" || true
  else
    echo "Secret $name not found — skipping grant"
  fi
done

echo "4) Trigger Cloud Build (build + deploy)"
gcloud builds submit --config cloudbuild.yaml --project="$PROJECT_ID" \
  --substitutions=_SERVICE_NAME="$SERVICE_NAME",_REGION="$REGION"

echo "Done. Monitor Cloud Run logs with: gcloud run logs read $SERVICE_NAME --region=$REGION --project=$PROJECT_ID"
