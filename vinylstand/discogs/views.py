from datetime import datetime
import pickle
import os.path

from django.conf import settings
from django.http import JsonResponse, HttpResponseNotFound
from django.shortcuts import render
from discogs_client import Client as DiscogsClient

from vinylstand.users.models import User


def init_client(user=None):
    client = DiscogsClient(
        user_agent=settings.USER_AGENT,
        consumer_key=settings.CONSUMER_KEY,
        consumer_secret=settings.CONSUMER_SECRET,
        token=user.auth_token,
        secret=user.auth_token_secret
    )
    return client


def profile(request, username=None):
    """
    Show the profile of a user.
    :param request: 
    :param username: Discogs username. When not provided, take the one of the current user.
    :return: 
    """

    # Check if a user with this username is registered.
    if username:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return HttpResponseNotFound('Discogs user {} not registered.'.format(username))
    else:
        user = request.user

    client = init_client(user.discogsuser)

    values = {}
    user = client.identity()
    user = client.user(user.username)
    values.update(get_user_values(user))
    values.update(get_user_collection(user))

    return render(request, 'discogs/profile.html', values)


def get_user_values(user):
    _ = user.profile

    values = user.data

    # Format registration date to datetime object.
    registered = values['registered'][:10]
    values.update({
        'registered': datetime.strptime(registered, "%Y-%m-%d"),
        'width': (82 * 10) + 20,
        'offset': 0
    })
    return values


def get_user_collection(user):
    # When we get the user's collection for the first time, we will pickle it after is loaded.
    # This is a first simple cache implementation. Must be improved!!!
    collection = get_saved_collection(user)

    if not collection:
        collection = []
        for folder in user.collection_folders:
            if folder.id == 0:
                for release in folder.releases:
                    collection.append(release)

        with open(user.username, 'wb') as output:
            pickle.dump(collection, output, pickle.HIGHEST_PROTOCOL)

    return {
        'releases': collection
    }


def get_saved_collection(user):
    # Check if there is a pickled file for this user.
    if not os.path.exists(user.username):
        return False

    print('File exists, unpickling...')
    with open(user.username, 'rb') as input:
        collection = pickle.load(input)
    return collection
