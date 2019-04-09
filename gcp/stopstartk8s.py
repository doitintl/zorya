import base64
from pprint import pprint
import json
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials

credentials = GoogleCredentials.get_application_default()

service = discovery.build('compute', 'v1', credentials=credentials)

# Project ID for this request.
project = 'MY-PROJECT-NAME'  # TODO: Update placeholder value.

# The name of the zone where the managed instance group is located.
zone = 'MY-ZONE'  # TODO: Update placeholder value.

filtre = '(labels.sched = on) AND (labels.type = k8s)'

# Arret
# Recherche de tous les groupes d'instance du projet pour la zone.
def stop_k8s(event, context):
    request = service.instanceGroupManagers().list(project=project, zone=zone)
    while request is not None:
        response = request.execute()

        for instance_group_manager in response['items']:
            # TODO: Change code below to process each `instance_group_manager` resource:
            #pprint(instance_group_manager)
            name = instance_group_manager['baseInstanceName']
            name = "%s-grp"%(name)
            print(name)
            # The number of running instances that the managed instance group should maintain at any given time.
            # The group automatically adds or removes instances to maintain the number of instances specified by
            # this parameter.
            size = 0  # TODO: Update placeholder value.

            request = service.instanceGroupManagers().resize(project=project, zone=zone, instanceGroupManager=name, size=size)
            response = request.execute()

            # TODO: Change code below to process the `response` dict:
            #pprint(response)
        request = service.instanceGroupManagers().list_next(previous_request=request, previous_response=response)
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    print(pubsub_message)
    
# Start
# Recherche de tous les groupes d'instance du projet pour la zone.
def start_k8s(event, context):
    request = service.instanceGroupManagers().list(project=project, zone=zone)
    while request is not None:
        response = request.execute()

        for instance_group_manager in response['items']:
            # TODO: Change code below to process each `instance_group_manager` resource:
            #pprint(instance_group_manager)
            name = instance_group_manager['baseInstanceName']
            name = "%s-grp"%(name)
            print(name)
            # The number of running instances that the managed instance group should maintain at any given time.
            # The group automatically adds or removes instances to maintain the number of instances specified by
            # this parameter.
            size = 1  # TODO: Update placeholder value.

            request = service.instanceGroupManagers().resize(project=project, zone=zone, instanceGroupManager=name, size=size)
            response = request.execute()

            # TODO: Change code below to process the `response` dict:
            #pprint(response)
        request = service.instanceGroupManagers().list_next(previous_request=request, previous_response=response)
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    print(pubsub_message)