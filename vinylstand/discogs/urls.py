from django.conf.urls import url

from .views import collection

app_name = 'discogs'

urlpatterns = [
    url(
        regex=r'^collection',
        view=collection,
        name='collection'
    ),
]
