# The project ID for the zorya deployment.
PROJECT_ID="chris-playground-297209"
# The region of the Cloud Run service.
REGION="us-west1"
# Zorya worker image
IMAGE_URL="gcr.io/chris-playground-297209/zorya2-worker"

# Do not change these variables
SERVICE_ACCOUNT_ID="zorya-worker"
SERVICE_NAME="zorya"
TOPIC_NAME="projects/${PROJECT_ID}/topics/zorya"
SUBSCRIPTION_NAME="projects/${PROJECT_ID}/subscriptions/zorya"
SCHEDULER_JOB="zorya"

# enable APIs
gcloud services enable --project $PROJECT_ID firestore.googleapis.com \
  run.googleapis.com \
  pubsub.googleapis.com \
  cloudscheduler.googleapis.com \
  compute.googleapis.com \
  sqladmin.googleapis.com

# create the zorya service account
gcloud iam service-accounts create $SERVICE_ACCOUNT_ID \
  --project $PROJECT_ID

# assign service account permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT_ID}@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/editor"

# deploy worker Cloud Run service
gcloud run deploy $SERVICE_NAME \
  --project $PROJECT_ID \
  --image $IMAGE_URL \
  --platform managed \
  --region $REGION \
  --no-allow-unauthenticated \
  --max-instances 1 \
  --service-account "${SERVICE_ACCOUNT_ID}@${PROJECT_ID}.iam.gserviceaccount.com"

# grant invoker role to service account
gcloud run services add-iam-policy-binding $SERVICE_NAME \
  --project $PROJECT_ID \
  --platform managed \
  --region $REGION \
  --member="serviceAccount:${SERVICE_ACCOUNT_ID}@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/run.invoker"

SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
  --project $PROJECT_ID \
  --platform managed \
  --region $REGION \
  --format="value(status.url)" \
)

# create Pub/Sub topic
gcloud pubsub topics create $TOPIC_NAME \
  --project $PROJECT_ID

# create Pub/Sub subscription
gcloud pubsub subscriptions create $SUBSCRIPTION_NAME \
  --project $PROJECT_ID \
  --topic=$TOPIC_NAME \
  --push-auth-service-account="${SERVICE_ACCOUNT_ID}@${PROJECT_ID}.iam.gserviceaccount.com" \
  --push-endpoint="${SERVICE_URL}/tasks/change_state"

gcloud projects add-iam-policy-binding chris-playground-297209 \
    --project chris-playground-297209 \
     --member=serviceAccount:service-555263590478@gcp-sa-pubsub.iam.gserviceaccount.com \
     --role=roles/iam.serviceAccountTokenCreator

# create Cloud Scheduler job
gcloud scheduler jobs create http $SCHEDULER_JOB \
  --project $PROJECT_ID \
  --schedule="0 * * * *" \
  --uri="${SERVICE_URL}/tasks/schedule" \
  --oidc-service-account-email="${SERVICE_ACCOUNT_ID}@${PROJECT_ID}.iam.gserviceaccount.com"
