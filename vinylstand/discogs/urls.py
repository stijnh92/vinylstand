from django.conf.urls import url

from .views import profile

app_name = 'discogs'

urlpatterns = [
    url(
        regex=r'^(?P<username>[\w.@+-]+)/$',
        view=profile,
        name='profile'
    ),
]
