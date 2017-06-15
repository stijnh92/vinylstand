from vinylstand.users.models import User

from .models import DiscogsUser


class DiscogsBackend(object):

    def authenticate(self, request=None, discogs_token=None):
        discogs_user = DiscogsUser.objects.filter(auth_token_secret=discogs_token)
        if discogs_user:
            return discogs_user[0].user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
