# zorya2

[![License](https://img.shields.io/github/license/doitintl/zorya.svg)](LICENSE)[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/release/python-360/)


Development resources are usually only needed during business hours. zorya is CLI and a tiny web application to schedule Google Cloud Platform resources. You can define schedules for Compute Engine instances, Cloud SQL instances, and Google Kubernetes Engine node pools with a visual UI.

The service architecture consists of:

- Cloud Run service exposing a REST API for the checks and tasks
- Firestore to persist policies, schedules, and settings
- Cloud Scheduler job for regular execution of the cheks
- Pub/Sub for task execution
- zorya CLI that starts a web server locally to configure policies and schedules stored in firestore

## How to

1. Create Google new Google Cloud project. (Recommended, see FAQ)
2. Install zorya via the Python package manager `pip`.
3. Install and authenticate the gcloud SDK on your local machine ([docs](https://cloud.google.com/sdk/docs/install)) and set your
4. 
5. Run `zorya env-setup to generate a bash script to deploy the zorya worker service to Cloud Run, and configure the other cloud resources like activating APIs, setting up Pub/Sub, etc. Run the command and wait until all steps have been completed.
6. Run `zorya env-check to verify the deployed environment.
7. Run `zorya start to start the local web server.
8. Open `http://localhost:8080` to open the zorya web UI.
9. Create a schedule first by specifying a name and the hours you want the resources to be up/down.
10. Create a policy by specifying a name, a comma separated list of projects where the policy should take effect, tags by which the resources are identified, and the schedule this should run on.
11. Every hour a job is checking all policies if the state of their schedule has changed. If yes, resources in the projects with the specified tags are started/stopped accordingly.

## Install the zorya CLI

zorya is a python-based command line interface and web server. Install it via the python package manager `pip`. Python 3.7 or higher is required.

```shell
python3 -m pip install zorya
```

## Supported resources

You can define schedules for the following resource types:

- Compute Engine Instances
- Cloud SQL instances
- Google Kubernetes Engine node pools
- Google App Engine flex instances (coming soon)

## Cost to run

Most of the elements are serverless and only used when running a check or running a task. Here is breakdown what elements charge what:

- Cloud Run: …
- Firestore: …
- Pub/Sub: …
- Cloud Scheduler: ...

## Permissions

The zorya worker service needs permission start/stop resources. The service is running with the service account `zorya-worker@{ZORYA_PROJECT_ID}.iam.gserviceaccount.com`. For every other Google Cloud project zorya should manage resources in run this command:

```shell
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member=serviceAccount:zorya-worker@${ZORYA_PROJECT_ID}.iam.gserviceaccount.com \
    --role=
```

## Frequently Asked Questions

### Why is the webserver not running in the cloud?

Because it doesn't have to. Running it locally is light-weight and suffiecient for most scenarios. Also, Cloud Run currently does not provide a simple and secure authentication method like IAP. Until that changes, you will have to fall back to zorya for a deployed web UI.

### Can I reuse an existing Google Cloud project instead of creating a new one?

We generally recommend creating a new one because it nicely separates the zorya resources from other resources. However, if you prefer to use an existing one, you can do that. The only requierement is that the Datastore API has not yet been activated.

## Python Development

zorya is using poetry for dependency management. Make sure it’s available in your environment by running:

```shell
poetry --version 
```

Open the repository and run:

```shell
# create virtual environment and install dependencies
poetry install
# format
poetry run black */**.py
# lint
poetry run flake8
# test
poetry run pytest
```

## Javascript Development

The zorya web UI is build with react.js and requires node.js and yarn. Make sure it’s available in your environment by running:

```shell
node --version
npm --version
yarn --version
```

Open the client folder and run:

```shell
# install dependencies
yarn install
# run dev server
yarn start
```

