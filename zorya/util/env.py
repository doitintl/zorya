"""env.py"""
import click
import requests.exceptions
import google.auth
from google.auth.transport.requests import AuthorizedSession
from google.cloud import pubsub

TASK_TOPIC = "zorya-tasks"
TASK_SBSCRIPTION = "zorya-tasks"
ZORYA_WORKER_SERVICE = "zorya-worker-service"
SERVICE_ACCOUNT_ID = "zorya"
SCHEDULER_JOB = "zorya"
API_SERVICES = [
    "firestore.googleapis.com",
    "run.googleapis.com",
    "pubsub.googleapis.com",
    "cloudscheduler.googleapis.com",
    "compute.googleapis.com",
    "sqladmin.googleapis.com",
]


class ZoryaEnvironment:
    service_name = ZORYA_WORKER_SERVICE

    def __init__(self, project_id) -> None:
        self.project_id = project_id

        credentials, _ = google.auth.default()
        self.service_account = (
            f"{SERVICE_ACCOUNT_ID}@{project_id}.iam.gserviceaccount.com"
        )
        self.publisher = pubsub.PublisherClient(credentials=credentials)
        self.subscriber = pubsub.SubscriberClient(credentials=credentials)
        self.topic_name = f"projects/{project_id}/topics/{TASK_TOPIC}"
        self.subscription_name = (
            f"projects/{project_id}/subscriptions/{TASK_SBSCRIPTION}"
        )
        self.authed_session = AuthorizedSession(credentials)

    def check_env(self):
        return (
            self.check_apis()
            and self.check_service_account()
            and self.check_worker()
            and self.check_scheduler()
            and self.check_subscription()
            and self.check_topic()
        )

    def check_env_full(self):
        env_okay = self.check_apis()
        env_okay = self.check_service_account()
        env_okay = self.check_worker()
        env_okay = self.check_scheduler()
        env_okay = self.check_subscription()
        env_okay = self.check_topic()
        return env_okay

    def check_apis(self):
        try:
            api_resp = self.authed_session.get(
                f"https://serviceusage.googleapis.com/v1/projects"
                f"/{self.project_id}/services?filter=state:ENABLED"
            )
            api_resp.raise_for_status()
        except requests.exceptions.HTTPError:
            click.echo("Service APIs: Cannot get enabled services")
            return False

        services = set(API_SERVICES)
        for service in api_resp.json().get("services", []):
            services.discard(service["name"].split("/").pop())

        if services:
            click.echo(f"Service APIs: Required APIs {services} not enabled")
            return False

        click.echo("Service APIs: check completed")
        return True

    def check_service_account(self):
        try:
            sa_resp = self.authed_session.get(
                f"https://iam.googleapis.com/v1/projects/{self.project_id}"
                "/serviceAccounts/{self.service_account}"
            )
            sa_resp.raise_for_status()
        except requests.exceptions.HTTPError:
            click.echo(
                "Service Account: Cannot get "
                f"service account {self.service_account}"
            )
            return False

        click.echo("Service Account: check completed")
        return True

    def check_service_account_role(self):
        try:
            iam_resp = self.authed_session.post(
                "https://cloudresourcemanager.googleapis.com/v1/projects"
                f"/{self.project_id}:getIamPolicy"
            )
            iam_resp.raise_for_status()

        except requests.exceptions.HTTPError:
            click.echo(
                "Service Account Role: cannot list project role bindings"
            )
            return

        for binding in iam_resp.json().get("bindings", []):
            if binding["role"] == "roles/editor":
                if self.service_account in binding["members"]:
                    click.echo("Service Account Project Role: check completed")
                    return True

        click.echo(
            "Service Account Role: Cannot find 'roles/editor' "
            f"binding for {self.service_account} on project"
        )
        return False

    def check_worker(self):
        try:
            services_resp = self.authed_session.get(
                (
                    "https://run.googleapis.com/apis/serving.knative.dev"
                    f"/v1/namespaces/{self.project_id}/services"
                )
            )
            services_resp.raise_for_status()
        except requests.exceptions.HTTPError:
            click.echo("Worker: Cannot list deployed Cloud Run services")
            return False

        for service in services_resp.json().get("items", []):
            if service["metadata"]["name"] == self.service_name:
                self.service_url = service["status"]["url"]

                if (
                    service["spec"]["template"]["spec"]["serviceAccountName"]
                    != self.service_account
                ):
                    click.echo(
                        "Worker: worker not using correct service account"
                    )
                    return False

                click.echo("Worker: check completed")
                return True

        click.echo(
            f"Worker: Cannot find Cloud Run service {self.service_name}"
        )
        return False

    def check_worker_iam(self):
        try:
            worker_iam_resp = self.authed_session.post(
                "https://run.googleapis.com/v1/projects"
                f"/{self.project_id}/locations/europe-west1/services"
                f"/{self.service_name}:getIamPolicy"
            )
            worker_iam_resp.raise_for_status()

        except requests.exceptions.HTTPError:
            click.echo("Worker IAM: Cannot list worker IAM bindings")
            return False

        for binding in worker_iam_resp.json().get("bindings", []):
            if binding["role"] == "roles/run.invoker":
                if self.service_account in binding["members"]:
                    click.echo("Worker IAM: check completed")
                    return True

        click.echo(
            f"Worker IAM: Service account {self.service_account} "
            "does not have 'roles.run/invoker' on worker service"
        )
        return False

    def check_scheduler(self):
        try:
            locations_resp = self.authed_session.get(
                "https://cloudscheduler.googleapis.com/v1/projects"
                f"/{self.project_id}/locations"
            )
            locations_resp.raise_for_status()

        except requests.exceptions.HTTPError:
            click.echo("Scheduler: Cannot list scheduler locations")
            return False

        try:
            for location in locations_resp.json().get("locations", []):
                location_resp = self.authed_session.get(
                    "https://cloudscheduler.googleapis.com/v1/projects"
                    f"/{self.project_id}/locations"
                    f"/{location['locationId']}/jobs"
                )
                location_resp.raise_for_status()
                for job in location_resp.json().get("jobs", []):
                    if job["name"].split("/").pop() == SCHEDULER_JOB:
                        click.echo("Scheduler: check completed")
                        return True

        except requests.exceptions.HTTPError:
            click.echo("Scheduler: Cannot list scheduler jobs")
            return False

        click.echo(f"Scheduler: Cannot find scheduler job {SCHEDULER_JOB}")
        return False

    def check_topic(self):
        try:
            self.publisher.get_topic(topic=self.topic_name)
        except google.api_core.exceptions.NotFound:
            click.echo(f"Topic: Connot find {self.topic_name!r}")
            return False

        click.echo("Topic: check completed")
        return True

    def check_subscription(self):
        try:
            subscription = self.subscriber.get_subscription(
                subscription=self.subscription_name
            )
        except google.api_core.exceptions.NotFound:
            click.echo(f"Subscription: Cannot find {self.subscription_name!r}")
            return False

        if (
            subscription.push_config.push_endpoint
            != f"{self.service_url}/tasks/change_state"
        ):
            click.echo(
                "Subscription: push_endpoint doesn't match "
                f"worker url {self.service_url}/tasks/change_state"
            )
            return False

        if (
            subscription.push_config.oidc_token.service_account_email
            != self.service_account
        ):
            click.echo(
                "Subscription: push_endpoint.oidc_token.service_account_email "
                f"doesn't match service account {self.service_account}"
            )
            return False

        click.echo("Subscription: check completed")
        return True
