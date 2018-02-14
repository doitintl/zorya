from gcp.compute import Compute

def change_state(tagkey,tagvalue, action, project):
    compute = Compute(project)
    compute.change_status(action, tagkey, tagvalue)
    return 'ok', 200