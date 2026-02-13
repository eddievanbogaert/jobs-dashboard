#!/usr/bin/env bash
# One-time GCP project bootstrap: enables APIs and creates Terraform state bucket.
set -euo pipefail

PROJECT_ID="${GCP_PROJECT_ID:-jobs-dashboard}"
REGION="${GCP_REGION:-us-central1}"
TF_STATE_BUCKET="${PROJECT_ID}-tf-state"

echo "==> Setting project to ${PROJECT_ID}"
gcloud config set project "${PROJECT_ID}"

echo "==> Enabling required APIs..."
APIS=(
  cloudfunctions.googleapis.com
  run.googleapis.com
  cloudbuild.googleapis.com
  cloudscheduler.googleapis.com
  bigquery.googleapis.com
  artifactregistry.googleapis.com
  secretmanager.googleapis.com
  iam.googleapis.com
  cloudresourcemanager.googleapis.com
)
for api in "${APIS[@]}"; do
  echo "    Enabling ${api}"
  gcloud services enable "${api}" --quiet
done

echo "==> Creating Terraform state bucket: gs://${TF_STATE_BUCKET}"
if gsutil ls -b "gs://${TF_STATE_BUCKET}" &>/dev/null; then
  echo "    Bucket already exists, skipping."
else
  gsutil mb -p "${PROJECT_ID}" -l "${REGION}" "gs://${TF_STATE_BUCKET}"
  gsutil versioning set on "gs://${TF_STATE_BUCKET}"
fi

echo "==> Creating FRED API key secret (you will need to add the secret version manually)"
if gcloud secrets describe fred-api-key --project="${PROJECT_ID}" &>/dev/null; then
  echo "    Secret already exists, skipping."
else
  gcloud secrets create fred-api-key --project="${PROJECT_ID}" --replication-policy="automatic"
  echo "    Secret created. Add your key with:"
  echo "    echo -n 'YOUR_FRED_API_KEY' | gcloud secrets versions add fred-api-key --data-file=-"
fi

echo ""
echo "==> Bootstrap complete!"
echo "    Next steps:"
echo "    1. Get a free FRED API key at https://fred.stlouisfed.org/docs/api/api_key.html"
echo "    2. Store it: echo -n 'YOUR_KEY' | gcloud secrets versions add fred-api-key --data-file=-"
echo "    3. Run: cd terraform && terraform init && terraform apply"
