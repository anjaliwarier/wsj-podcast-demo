#!/bin/bash
# schedule_pipeline.sh
# Automates the deployment of a Cloud Scheduler job to invoke the Agent Pipeline daily.

PROJECT_ID=$(gcloud config get-value project)
LOCATION="us-central1"
SERVICE_ACCOUNT="podcast-agent-sa@${PROJECT_ID}.iam.gserviceaccount.com"

# 1. Retrieve the latest Reasoning Engine Resource ID
echo "Fetching active Reasoning Engine endpoints..."
RESOURCE_ID=$(gcloud ai reasoning-engines list --project=${PROJECT_ID} --region=${LOCATION} --format="value(name)" | head -n 1)

if [ -z "$RESOURCE_ID" ]; then
    echo "No Reasoning Engine deployed. Run 'python deployment/deploy.py --create' first."
    exit 1
fi

echo "Found Endpoint: $RESOURCE_ID"
ENDPOINT_URL="https://${LOCATION}-aiplatform.googleapis.com/v1beta1/${RESOURCE_ID}:query"

# 2. Deploy Cloud Scheduler
echo "Deploying daily Cloud Scheduler Job..."
gcloud scheduler jobs create http wsj-podcast-daily-trigger \
    --location=${LOCATION} \
    --schedule="0 6 * * *" \
    --uri="${ENDPOINT_URL}" \
    --http-method=POST \
    --message-body='{"input": {"prompt": "Run daily pipeline"}}' \
    --headers="Content-Type=application/json" \
    --oauth-service-account-email=${SERVICE_ACCOUNT}

echo "Done! The WSJ Agent will now execute automatically every day at 6:00 AM."
