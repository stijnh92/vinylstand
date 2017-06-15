from django.conf.urls import url

from .views import test, callback, identity

urlpatterns = [
    url(
        regex=r'^$',
        view=test,
        name='test'
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
]
