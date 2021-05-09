"""cli.py"""
import os
import click

import google.auth
import google.api_core.exceptions

from zorya.app import StandaloneApplication
from zorya.util.env import ZoryaEnvironment


_, PROJECT = google.auth.default()


@click.group()
def cli():
    pass


@cli.command()
@click.option("--project", default=PROJECT)
def start(project):
    """Start a local webserver to configure the scheduler."""
    os.environ["ZORYA_PROJECT"] = project

    click.echo(
        f"""
  ________  ______   __ _    
 |__  / _ \|  _ \ \ / // \   
   / / | | | |_) \ V // _ \  
  / /| |_| |  _ < | |/ ___ \ 
 /____\___/|_| \_\|_/_/   \_\ 
                             

Zorya CLI Version beta-1

Running with project {project!r}
"""  # noqa
    )
    env = ZoryaEnvironment(project)
    env_okay = env.check_env()

    if not env_okay:
        click.confirm(
            """
The environemnt has erros. Zorya will not work as expected.
Please run `zorya env-setup` for setup information.

Do you want to continue?
""",
            abort=True,
        )

    options = {
        "bind": "%s:%s" % ("127.0.0.1", "8080"),
        "workers": 1,
    }
    StandaloneApplication(options).run()


@cli.command()
@click.option("--project", default=PROJECT)
def env_check(project):
    """
    Run the full environment check.
    """
    env = ZoryaEnvironment(project)
    env_okay = env.check_env_full()

    if not env_okay:
        click.echo(
            """
The environemnt has erros. Zorya will not work as expected.
Please run `zorya env-setup` for setup information.
""",
        )


@cli.command()
@click.option("--project", default=PROJECT)
def env_setup(project):
    """
    Generate a shell script to configure your Zorya environment.
    """
    click.echo(
        f"Run the following script to configure your project '{project}'"
    )
    click.echo(
        f"""# The project ID for the zorya deployment.
PROJECT_ID="{project}"
"""
        """# The region of the Cloud Run service.
REGION="us-west1"
# Zorya worker image
IMAGE_URL =""

# Do not change these variables
SERVICE_ACCOUNT_ID="zorya"
SERVICE_NAME="zorya"
TOPIC_NAME="projects/${PROJECT_ID}/topics/zorya"
SUBSCRIPTION_NAME=TOPIC_NAME="projects/${PROJECT_ID}/subscriptions/zorya"
SCHEDULER_JOB="zorya"

# enable APIs
gcloud services enable firestore.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable pubsub.googleapis.com
gcloud services enable cloudscheduler.googleapis.com
gcloud services enable compute.googleapis.com
gcloud services enable sqladmin.googleapis.com

# create the zorya service account
gcloud iam service-accounts create $SERVICE_ACCOUNT_ID \\
  --display-name="DISPLSERVICE_ACCOUNT_IDAY_NAME"

# assign service account permissions
gcloud projects add-iam-policy-binding PROJECT_ID \\
  --member="serviceAccount:${SERVICE_ACCOUNT_ID}@${PROJECT_ID}.iam.gserviceaccount.com" \\
  --role="role/editor"

# deploy worker Cloud Run service
gcloud run deploy zorya --image $IMAGE_URL \\
  --platform managed \\
  --region $REGION

# grant invoker role to service account
gcloud run services add-iam-policy-binding $SERVICE_NAME \\
  --member="serviceAccount:${SERVICE_ACCOUNT_ID}@${PROJECT_ID}.iam.gserviceaccount.com" \\
  --role="roles/run.invoker"

SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \\
  --platform managed \\
  --region europe-west1 \\
  --format="value(status.url)" \\
)

# create Pub/Sub topic
gcloud pubsub topcis create $TOPIC_NAME

# create Pub/Sub subscription
gcloud pubsub subscriptions create $SUBSCRIPTION_NAME \\
  --topic=$TOPIC_NAME \\
  --max-delivery-attempts=3 \\
  --push-auth-service-account="${SERVICE_ACCOUNT_ID}@${PROJECT_ID}.iam.gserviceaccount.com" \\
  --push-endpoint="${SERVICE_URL}/tasks/change_state"

# create Cloud Scheduler job
gcloud scheduler jobs create http $SCHEDULER_JOB \\
  --schedule="0 * * * *" \\
  --uri="${SERVICE_URL}/tasks/schedule" \\
  --oidc-service-account-email="${SERVICE_ACCOUNT_ID}@${PROJECT_ID}.iam.gserviceaccount.com"
"""  # noqa
    )


if __name__ == "__main__":
    cli()
