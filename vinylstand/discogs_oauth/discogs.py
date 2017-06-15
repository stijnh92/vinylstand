from discogs_client.models import User as DiscogsUser
from discogs_client.models import SimpleField


class User(DiscogsUser):
    email = SimpleField()
