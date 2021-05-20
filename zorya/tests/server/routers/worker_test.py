import json
import base64
from unittest import mock

from fastapi.testclient import TestClient

from zorya.server.main import app
from zorya.models.state_change import StateChange

client = TestClient(app, raise_server_exceptions=True)


def encode_json(data):
    json_str = json.dumps(data)
    json_str_encoded = json_str.encode("utf-8")
    return base64.b64encode(json_str_encoded).decode("utf-8")


# @mock.patch("zorya.tasks.policy.change_state")
# def test_task_success(change_state_mock: mock.Mock):
#     raw_data = {
#         "tagkey": "tagkey",
#         "tagvalue": "tagvalue",
#         "action": 1,
#         "project": "project",
#     }

#     response = client.post(
#         "/task",
#         json={
#             "subscription": "projects/project-id/subscriptions/zorya",
#             "message": {
#                 "data": encode_json(raw_data),
#                 "publish_time": "2021-05-10T18:03:53.03Z",
#                 "message_id": "2362980386958601",
#             },
#         },
#     )

#     assert change_state_mock.call_args[0] == (StateChange(**raw_data),)

#     assert response.status_code == 200


# @mock.patch("zorya.tasks.policy.change_state", side_effect=Exception())
# def test_task_error(change_state_mock: mock.Mock):
#     response = client.post(
#         "/task",
#         json={
#             "subscription": "projects/project-id/subscriptions/zorya",
#             "message": {
#                 "data": encode_json(
#                     {
#                         "tagkey": "tagkey",
#                         "tagvalue": "tagvalue",
#                         "action": 1,
#                         "project": "project",
#                     }
#                 ),
#                 "publish_time": "2021-05-10T18:03:53.03Z",
#                 "message_id": "2362980386958601",
#             },
#         },
#     )
#     assert response.status_code == 500


# @mock.patch("zorya.tasks.schedule.check_all")
# def test_schedule_success(check_all_mock: mock.Mock):
#     response = client.get("/schedule")
#     assert response.status_code == 200, response.text
#     check_all_mock.assert_called_once()


# @mock.patch("zorya.tasks.schedule.check_all", side_effect=Exception())
# def test_schedule_error(check_all_mock):
#     response = client.get("/schedule")
#     assert response.status_code == 500
