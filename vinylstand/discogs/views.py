from django.conf import settings
from django.http import JsonResponse
from discogs_client import Client as DiscogsClient

CONSUMER_KEY = settings.CONSUMER_KEY
CONSUMER_SECRET = settings.CONSUMER_SECRET
CALLBACK_URL = settings.CALLBACK_URL
USER_AGENT = settings.USER_AGENT


def init_client(request):
    client = DiscogsClient(
        USER_AGENT,
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        token=request.user.discogsuser.auth_token,
        secret=request.user.discogsuser.auth_token_secret
    )
    return client


def identity(request):
    client = init_client(request)

    user = client.identity()
    user = client.user(user.username)
    _ = user.profile

    return JsonResponse(user.data)


def collection(request):
    client = init_client(request)
    user = client.identity()

    folder = user.collection_folders[0]

    return JsonResponse({
        'inventory': len(user.inventory),
        'wantlist': len(user.wantlist),
        'folders': str(user.collection_folders),
        'releases': len(folder.releases.page(1))
    })
