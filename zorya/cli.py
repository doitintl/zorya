"""cli.py"""
import os
import click

import google.auth
from google.auth.transport.requests import AuthorizedSession
from google.cloud import pubsub

from zorya.app import StandaloneApplication
from zorya.util import utils

TASK_TOPIC = "zorya_tasks"
TASK_SBSCRIPTION = "zorya_tasks"
ZORYA_WORKER_SERVICE = "zorya_worker_service"
_, PROJECT = google.auth.default()


@click.option("--project", default=PROJECT)
@click.command()
def cli(project):
    """Zorya CLI starts a local webserver to configure the scheduler."""
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

Checking your environment ...

"""  # noqa
    )
    options = {
        "bind": "%s:%s" % ("127.0.0.1", "8080"),
        "workers": 1,
    }
    StandaloneApplication(options).run()


class ZoryaEnvironment:
    service_name = ZORYA_WORKER_SERVICE

    def __init__(self) -> None:
        credentials, project_id = google.auth.default()
        self.publisher = pubsub.PublisherClient(
            credentials=credentials, project=project_id
        )
        self.subscriber = pubsub.SubscriberClient(
            credentials=credentials, project=project_id
        )
        self.topic_name = f"projects/{project_id}/topics/{TASK_TOPIC}"
        self.subscription_name = (
            f"projects/{project_id}/subscriptions/{TASK_SBSCRIPTION}"
        )
        self.authed_session = AuthorizedSession(credentials)

    def check_worker(self):
        click.echo("Checking worker service ...")
        try:
            services_resp = self.authed_session.get(
                (
                    "https://run.googleapis.com/apis/serving.knative.dev"
                    f"/v1/namespaces/{self.project_id}/services"
                )
            )
            services = services_resp.json()["items"]
            for service in services:
                if service["metadata"]["name"] == self.service_name:
                    self.service_account = service["spec"]["template"]["spec"][
                        "serviceAccountName"
                    ]
                    self.service_url = service["status"]["url"]
                    return

        except:  # noqa
            pass

        click.echo("Cannot find deployed worker. Make sure you ran the setup.")
        raise click.Abort()

    def check_topic(self):
        click.echo("Checking pub/sub topic ...")

        try:
            self.publisher.get_topic(self.topic_name)
            return

        except Exception as e:
            print(e)

            click.echo(f"Topic {self.topic_name!r} not found.")
            raise click.Abort()

    def check_subscription(self):
        click.echo("Checking pub/sub subscription ...")

        try:
            self.subscriber.get_subscription(self.subscription_name)
            return

        except Exception as e:
            print(e)

        click.echo(f"Topic {self.subscription_name!r} not found.")
        raise click.Abort()


if __name__ == "__main__":
    cli()
