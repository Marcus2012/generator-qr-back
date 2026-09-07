#!/bin/bash

# Google Cloud Run Deployment Script
# This script automates the deployment of the QR Generator backend to Google Cloud Run
# Prerequisites:
#   - gcloud CLI installed: https://cloud.google.com/sdk/docs/install
#   - Docker installed for local testing
#   - Authenticated: gcloud auth login
#   - Project set: gcloud config set project PROJECT_ID

set -e

# Configuration
SERVICE_NAME="${1:-qr-backend}"
REGION="${2:-us-central1}"
PROJECT_ID="${3:-$(gcloud config get-value project)}"
SERVICE_ACCOUNT="${SERVICE_ACCOUNT:-qr-backend-signer@${PROJECT_ID}.iam.gserviceaccount.com}"
IMAGE_URL="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🚀 Google Cloud Run Deployment${NC}"
echo "=================================="
echo "Service Name: $SERVICE_NAME"
echo "Region: $REGION"
echo "Project ID: $PROJECT_ID"
echo "Image URL: $IMAGE_URL"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
    echo -e "${RED}❌ Not authenticated. Run 'gcloud auth login' first.${NC}"
    exit 1
fi

echo -e "${YELLOW}1️⃣  Building Docker image...${NC}"
docker build -t ${IMAGE_URL}:latest .
docker build -t ${IMAGE_URL}:$(date +%Y%m%d-%H%M%S) .

echo -e "${YELLOW}2️⃣  Pushing image to Google Container Registry...${NC}"
docker push ${IMAGE_URL}:latest

echo -e "${YELLOW}3️⃣  Deploying to Cloud Run...${NC}"
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_URL}:latest \
    --region ${REGION} \
    --platform managed \
    --memory 512Mi \
    --cpu 1 \
    --timeout 300 \
    --max-instances 10 \
    --min-instances 0 \
    --concurrency 80 \
    --allow-unauthenticated \
    --service-account ${SERVICE_ACCOUNT} \
    --set-env-vars PYTHONUNBUFFERED=1,GOOGLE_APPLICATION_CREDENTIALS=/secrets/gcp-key.json \
    --set-secrets /secrets/gcp-key.json=GCP_SERVICE_ACCOUNT_KEY:latest,\
DB_USER=DB_USER:latest,\
DB_PASSWORD=DB_PASSWORD:latest,\
DB_HOST=DB_HOST:latest,\
DB_PORT=DB_PORT:latest,\
DB_NAME=DB_NAME:latest,\
SECRET_KEY=SECRET_KEY:latest,\
ALGORITHM=ALGORITHM:latest,\
ACCESS_TOKEN_EXPIRE_MINUTES=ACCESS_TOKEN_EXPIRE_MINUTES:latest,\
GCP_PROJECT_ID=GCP_PROJECT_ID:latest,\
GCP_BUCKET_NAME=GCP_BUCKET_NAME:latest,\
BACKEND_PUBLIC_URL=BACKEND_PUBLIC_URL:latest \
    --format json

echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo ""
echo "To view logs:"
echo "  gcloud run logs read ${SERVICE_NAME} --region ${REGION}"
echo ""
echo "To check the service:"
echo "  gcloud run services describe ${SERVICE_NAME} --region ${REGION}"
echo ""
echo "To get the service URL:"
echo "  gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format='value(status.url)'"
