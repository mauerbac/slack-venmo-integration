from django.db import models
from django.contrib.auth.models import User


class NumberMap(models.Model):
    
    phone_number = models.CharField(max_length=12)
    slack_username = models.CharField(max_length=75)

class Requestor(models.Model):

    slack_username = models.CharField(max_length=200, default="")
    slack_user_id = models.CharField(max_length=200)
    venmo_auth_token = models.CharField(max_length=200)
    active = models.BooleanField(default=False)


