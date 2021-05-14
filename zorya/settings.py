import google.auth
import pydantic


class ZoryaSettings(pydantic.BaseModel):
    project_id: str = pydantic.Field(
        default_factory=lambda: google.auth.default()[1]
    )
    task_uri: str = "/task"
    scheduler_uri: str = "/schedule"
    service_account_id: str = "zorya-worker"
    service_name: str = "zorya"
    topic_id: str = "zorya"
    subscription_id: str = "zorya"
    scheduler_name: str = "zorya"
    image_url: str = "gcr.io/chris-playground-297209/zorya2-worker"
    cloud_run_region: str = "us-west1"
    scheduler_schedule: str = "0 * * * *"


settings = ZoryaSettings()
