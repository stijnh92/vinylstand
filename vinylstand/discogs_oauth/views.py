import os

from django.conf import settings
from django.contrib.auth import login
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from discogs_client import Client as DiscogsClient

from vinylstand.users.models import User

from .models import Token, DiscogsUser
from .backend import DiscogsBackend

CONSUMER_KEY = settings.CONSUMER_KEY
CONSUMER_SECRET = settings.CONSUMER_SECRET

CALLBACK_URL = 'http://090f6be2.ngrok.io/discogs/oauth/callback'

USER_AGENT = 'vinylstand/1.0'


def authorize(request):
    client = DiscogsClient(USER_AGENT, consumer_key=CONSUMER_KEY, consumer_secret=CONSUMER_SECRET)
    access_token, access_secret, authorize_url = client.get_authorize_url(callback_url=CALLBACK_URL)

    # Save the secret access so we can use it in our callback method.
    # This will be identified by the access_token we received now.
    token = Token(
        identifier=access_token,
        secret_token=access_secret
    )
    token.save()

    # Redirect the user to the Discogs authorize URL.
    return redirect(authorize_url)


def callback(request):
    result = request.GET

    if 'oauth_token' not in result or 'oauth_verifier' not in result:
        return HttpResponse('Error verifying your Discogs account.', status=500)

    oauth_token = result['oauth_token']
    oauth_verifier = result['oauth_verifier']

    # Get the secret access we retrieved in the request token step.
    token = Token.objects.get(identifier=oauth_token)

    # Now initialize a new Client instance with the secret token set.
    client = DiscogsClient(USER_AGENT, consumer_key=CONSUMER_KEY, consumer_secret=CONSUMER_SECRET,
                           token=oauth_token, secret=token.secret_token)

    access_token, access_secret = client.get_access_token(oauth_verifier)

    discogs_user = get_discogs_user(client, access_token, access_secret)

    # Authenticate and log the user in.
    db = DiscogsBackend()
    user = db.authenticate(request=request, discogs_token=discogs_user.auth_token_secret)

    auth_backend = 'vinylstand.discogs_oauth.backend.DiscogsBackend'
    login(request, user, backend=auth_backend)

    return redirect('home')


def get_discogs_user(discogs_client, access_token, access_secret):
    discogs_identity = discogs_client.identity()
    username = discogs_identity.username

    try:
        # Check if this user has already authenticated with Discogs.
        user = User.objects.get(username=username)
        discogs_user = user.discogsuser
    except User.DoesNotExist:
        # Create a new user.
        discogs_user_data = discogs_client.user(username)

        # First, create a new user which can be used for authentication in a later phase.
        user = User.objects.create_user(
            username=username,
            name=discogs_user_data.name,
            email=discogs_user_data.data['email']
        )
        user.save()

        # When a basic user is created, create a new Discogs user that stores the access token and secret.
        discogs_user = DiscogsUser(
            user_id=user.id,
            auth_token=access_token,
            auth_token_secret=access_secret
        )
        discogs_user.save()

    return discogs_user


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
