"""cli.py"""
import click
import uvicorn

from zorya.cli.env import ZoryaEnvironment
from zorya.settings import settings


def set_setting(ctx, param, value):
    settings.__setattr__(param.name, value)
    return value


@click.group()
def cli():
    pass


@cli.command()
@click.option("--port", default=8080, type=int)
@click.option(
    "--project_id", callback=set_setting, default=settings.project_id
)
def start(project_id, port):
    """Start a local webserver to configure the scheduler."""

    click.echo(
        f"""
  ________  ______   __ _    
 |__  / _ \|  _ \ \ / // \   
   / / | | | |_) \ V // _ \  
  / /| |_| |  _ < | |/ ___ \ 
 /____\___/|_| \_\|_/_/   \_\ 
                             

Zorya CLI Version beta-1

Running with project {project_id!r}
"""  # noqa
    )
    env = ZoryaEnvironment(project_id)
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

    click.echo("Starting zorya webserver locally ...")

    from zorya.server.main import app

    uvicorn.run(app, host="0.0.0.0", port=port)


@cli.command()
@click.option(
    "--project_id", callback=set_setting, default=settings.project_id
)
def env_check(project_id):
    """
    Run the full environment check.
    """
    env = ZoryaEnvironment(project_id)
    env_okay = env.check_env_full()

    if not env_okay:
        click.echo(
            """
The environemnt has erros. Zorya will not work as expected.
Please run `zorya env-setup` for setup information.
""",
        )


@cli.command()
@click.option("--project", callback=set_setting, default=settings.project_id)
def env_setup(project_id):
    """
    Generate a shell script to configure your Zorya environment.
    """
    click.echo(
        f"Run the following script to configure your project {project_id!r}"
    )
    header = """
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

""".format(
        **settings.dict()
    )
    click.echo(
        header
        + """
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
