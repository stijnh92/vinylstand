from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session
from django.http import HttpResponse, JsonResponse

import requests_oauthlib
from urllib.parse import parse_qsl
from discogs_client import Client

from .models import Token, DiscogsUser

CONSUMER_KEY = 'tiijtdeltoxNIyGmgmvf'
CONSUMER_SECRET = 'tLSGuhBPVoeIQcwjrmFggriMYMhhLslb'

OAUTH_URL = 'https://api.discogs.com/oauth/'
REQUEST_TOKEN_URL = OAUTH_URL + 'request_token'
ACCESS_TOKEN_URL = OAUTH_URL + 'access_token'
AUTHORIZE_URL = 'https://discogs.com/oauth/authorize?oauth_token={}'


USER_AGENT = 'vinylstand/1.0'


def test(request):
    session = requests_oauthlib.OAuth1Session(
        client_key=CONSUMER_KEY,
        client_secret=CONSUMER_SECRET,
        callback_uri='https://9d91e30e.ngrok.io/discogs/oauth/callback'
    )
    response = session.get(REQUEST_TOKEN_URL)
    result = dict(parse_qsl(response.content))

    oauth_token_secret = result[b'oauth_token_secret'].decode('utf-8')
    oauth_token = result[b'oauth_token'].decode('utf-8')

    # save the token
    token = Token(
        identifier=oauth_token,
        secret_token=oauth_token_secret
    )
    token.save()

    authorize_url = AUTHORIZE_URL.format(oauth_token)
    url = '<a href={}>Click here </a>'.format(authorize_url)

    return HttpResponse(url)


def callback(request):
    result = request.GET

    oauth_token = result['oauth_token']
    oauth_verifier = result['oauth_verifier']

    token = Token.objects.get(identifier=oauth_token)

    session = requests_oauthlib.OAuth1Session(
        client_key=CONSUMER_KEY,
        client_secret=CONSUMER_SECRET,
        verifier=oauth_verifier,
        resource_owner_key=oauth_token,
        resource_owner_secret=token.secret_token
    )
    response = session.post(ACCESS_TOKEN_URL)
    result = dict(parse_qsl(response.content))

    oauth_token_secret = result[b'oauth_token_secret'].decode('utf-8')
    oauth_token = result[b'oauth_token'].decode('utf-8')

    # TODO: Store everything here.
    discogs_user = DiscogsUser(
        auth_token=oauth_token,
        auth_token_secret=oauth_token_secret
    )
    discogs_user.save()

    return HttpResponse('Authenticated!')


def identity(requets):

    d = Client(USER_AGENT)
    d.set_consumer_key(CONSUMER_KEY, CONSUMER_SECRET)

    # Get a discogs user
    discogs_users = DiscogsUser.objects.all()
    discogs_user = discogs_users[0]

    d.set_token(discogs_user.auth_token, discogs_user.auth_token_secret)

    user = d.identity()
    user = d.user(user.username)

    # We must first fetch the profile before accessing some extra fields.
    _ = user.profile

    return JsonResponse(user.data)
