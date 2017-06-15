from django.conf.urls import url

from .views import *

app_name = 'discogs_oauth'

urlpatterns = [
    url(
        regex=r'^authorize$',
        view=authorize,
        name='authorize'
    ),
    url(
        regex=r'^callback$',
        view=callback,
        name='callback'
    ),
    url(
        regex=r'^identity',
        view=identity,
        name='identity'
    ),
    url(
        regex=r'^collection',
        view=collection,
        name='collection'
    ),
]
