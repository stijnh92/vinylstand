from django.db import models
from vinylstand.users.models import User


class Token(models.Model):
    identifier = models.CharField(max_length=256)
    secret_token = models.CharField(max_length=256)


class DiscogsUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    auth_token = models.CharField(max_length=256)
    auth_token_secret = models.CharField(max_length=256)
