REGION="us-west1"
IMAGE_URL =""
PROJECT_ID=$(gcloud config get-value project)
SERVICE_ACCOUNT_ID="zorya"
SERVICE_NAME="zorya"
TOPIC_NAME="projects/${PROJECT_ID}/topics/zorya"
SUBSCRIPTION_NAME=TOPIC_NAME="projects/${PROJECT_ID}/subscriptions/zorya"
SCHEDULER_JOB="zorya"

# enable APIs ...
# ...

# create the zorya service account
gcloud iam service-accounts create $SERVICE_ACCOUNT_ID \
  --display-name="DISPLSERVICE_ACCOUNT_IDAY_NAME"

# assign service account permissions
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT_ID}@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="role/editor"

# deploy worker Cloud Run service
gcloud run deploy zorya --image $IMAGE_URL \
  --platform managed \
  --region $REGION

# grant invoker role to service account
gcloud run services add-iam-policy-binding $SERVICE_NAME \
  --member="serviceAccount:${SERVICE_ACCOUNT_ID}@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/run.invoker"

SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
  --platform managed \
  --region europe-west1 \
  --format="value(status.url)" \
)

# create Pub/Sub topic
gcloud pubsub topcis create $TOPIC_NAME

# create Pub/Sub subscription
gcloud pubsub subscriptions create $SUBSCRIPTION_NAME \
  --topic=$TOPIC_NAME \
  --max-delivery-attempts=3 \
  --push-auth-service-account="${SERVICE_ACCOUNT_ID}@${PROJECT_ID}.iam.gserviceaccount.com" \
  --push-endpoint="${SERVICE_URL}/tasks/change_state"

# create Cloud Scheduler job
gcloud scheduler jobs create http $SCHEDULER_JOB \
  --schedule="0 * * * *" \
  --uri="${SERVICE_URL}/tasks/schedule" \
  --oidc-service-account-email="${SERVICE_ACCOUNT_ID}@${PROJECT_ID}.iam.gserviceaccount.com"
