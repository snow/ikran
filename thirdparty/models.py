from django.db import models
from django.contrib.auth.models import User

class TwitterAccount(models.Model):
    '''A twitter account that linked with a django user'''
    # override default AutoField pk to force id to be assigned
    id = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=255)
    key = models.CharField(max_length=255)
    secret = models.CharField(max_length=255)
    
    user = models.ForeignKey(User, unique=True)
