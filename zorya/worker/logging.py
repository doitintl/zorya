"""logging.py"""
import json
from copy import copy

import requests
from fastapi import Request


# def cloud_logger(
#     message,
#     request: Request = None,
#     severity="NOTICE",
#     **kwarags,
# ):
#     if not runtime_project_id:
#         logging.info(message)
#         return

#     trace_header = None
#     if request:
#         trace_header = request.headers.get("X-Cloud-Trace-Context")

#     if trace_header:
#         trace = trace_header.split("/")
#         kwarags[
#             "logging.googleapis.com/trace"
#         ] = f"projects/{runtime_project_id}/traces/{trace[0]}"

#     entry = dict(
#         severity=severity,
#         message=message,
#         **kwarags,
#     )

#     print(json.dumps(entry))


class Logger:
    def __init__(self, request: Request = None, **kwargs):
        self.request = request
        self.kwargs = kwargs

    def refine(self, **kwargs):
        new = copy(self)
        new.kwargs = {**new.kwargs, **kwargs}
        return new

    def __call__(
        self,
        message,
        severity="NOTICE",
        **kwarags,
    ):
        if not self.runtime_project_id:
            print(message)
            return

        trace_header = None
        if self.request:
            trace_header = self.request.headers.get("X-Cloud-Trace-Context")

        if trace_header:
            trace = trace_header.split("/")
            kwarags[
                "logging.googleapis.com/trace"
            ] = f"projects/{self.runtime_project_id}/traces/{trace[0]}"

        entry = dict(
            severity=severity,
            message=message,
            **self.kwargs,
            **kwarags,
        )

        print(json.dumps(entry))

    @property
    def runtime_project_id(self):
        try:
            project_request = requests.get(
                "http://metadata.google.internal/computeMetadata/v1/project/project-id",
                headers={"Metadata-Flavor": "Google"},
            )
            return project_request.text
        except:  # noqa
            return None
