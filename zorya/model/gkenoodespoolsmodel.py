"""DB model GKE node pools."""
from google.cloud import ndb


class GkeNodePoolModel(ndb.Model):
    """Class that represents Number of nodes in a nodepool."""

    Name = ndb.StringProperty(indexed=True, required=True)
    NumberOfNodes = ndb.IntegerProperty(required=True)
