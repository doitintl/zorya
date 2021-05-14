# The project ID for the zorya deployment.
PROJECT_ID="{project_id}"
# The region of the Cloud Run service.
REGION="{cloud_run_region}"
# Zorya worker image
IMAGE_URL="{image_url}"

# Do not change these variables
TASK_URI="{task_uri}"
SERVICE_ACCOUNT_ID="{service_account_id}"
SERVICE_NAME="{service_name}"
TOPIC_NAME="projects/$PROJECT_ID/topics/{topic_id}"
SUBSCRIPTION_NAME="projects/$PROJECT_ID/subscriptions/{subscription_id}"
SCHEDULER_NAME="{scheduler_name}"
SCHEDULER_SCHEDULE="{scheduler_schedule}"

PROJECT_NUMBER=$(gcloud projects list --filter=$PROJECT_ID --format="value(project_number)")

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

# create Pub/Sub topic
gcloud pubsub topics create $TOPIC_NAME \
  --project $PROJECT_ID

SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
  --project $PROJECT_ID \
  --platform managed \
  --region $REGION \
  --format="value(status.url)" \
)

# create Pub/Sub subscription
gcloud pubsub subscriptions create $SUBSCRIPTION_NAME \
  --project $PROJECT_ID \
  --topic=$TOPIC_NAME \
  --push-auth-service-account="${SERVICE_ACCOUNT_ID}@${PROJECT_ID}.iam.gserviceaccount.com" \
  --push-endpoint="${SERVICE_URL}${TASK_URI}"

# grant Pub/Sub service account permission to generate tokens from service account
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --project $PROJECT_ID \
  --member="serviceAccount:service-${PROJECT_NUMBER}@gcp-sa-pubsub.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountTokenCreator"

# create Cloud Scheduler job
gcloud scheduler jobs create http $SCHEDULER_NAME \
  --project $PROJECT_ID \
  --schedule=$SCHEDULER_SCHEDULE \
  --uri="${SERVICE_URL}${scheduler_uri}" \
  --oidc-service-account-email="${SERVICE_ACCOUNT_ID}@${PROJECT_ID}.iam.gserviceaccount.com"
