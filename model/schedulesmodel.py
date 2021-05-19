"""Database representation of schedule."""

from google.cloud import ndb

from util import tz


class SchedulesModel(ndb.Model):
    """Stores scheduling data."""
    Name = ndb.StringProperty(indexed=True, required=True)
    DisplayName = ndb.StringProperty(indexed=True, required=False)
    Timezone = ndb.StringProperty(
        default='UTC', choices=tz.get_all_timezones(), required=True)
    Schedule = ndb.JsonProperty(required=True)
