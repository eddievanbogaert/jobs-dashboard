#!/usr/bin/env bash
# Manually trigger a full historical backfill of FRED data.
set -euo pipefail

PROJECT_ID="${GCP_PROJECT_ID:-jobs-dashboard}"
REGION="${GCP_REGION:-us-central1}"

INGEST_URL=$(gcloud functions describe ingest-fred \
  --gen2 --region="${REGION}" --project="${PROJECT_ID}" \
  --format='value(serviceConfig.uri)')

echo "==> Triggering full backfill via ${INGEST_URL}"
curl -s -X POST "${INGEST_URL}" \
  -H "Authorization: bearer $(gcloud auth print-identity-token)" \
  -H "Content-Type: application/json" \
  -d '{"backfill": true, "observation_start": "2000-01-01"}' | jq .

echo ""
echo "==> Backfill request sent. Check Cloud Logging for progress."

TRANSFORM_URL=$(gcloud functions describe transform-analytics \
  --gen2 --region="${REGION}" --project="${PROJECT_ID}" \
  --format='value(serviceConfig.uri)')

echo "==> Triggering analytics transform via ${TRANSFORM_URL}"
curl -s -X POST "${TRANSFORM_URL}" \
  -H "Authorization: bearer $(gcloud auth print-identity-token)" \
  -H "Content-Type: application/json" \
  -d '{}' | jq .

echo "==> Done."
