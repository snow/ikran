from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend
from django.conf import settings
from tweepy import OAuthHandler, API

class DuplicatedUsername(Exception):
    '''Username got from openid/oauth provider was taken here'''
    def __init__(self, username):
        self.message = 'username "{}" was taken'.format(username)

class TwitterAccount(models.Model):
    '''A twitter account that linked with a django user'''
    # override default AutoField pk to force id to be assigned
    id = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=255)
    fullname = models.CharField(max_length=255)
    
    key = models.CharField(max_length=255)
    secret = models.CharField(max_length=255)
    
    user = models.ForeignKey(User, unique=True)
    
            
class GoogleAccount(models.Model):
    '''A google account that linked with a django user'''
    username = models.CharField(max_length=255)
    fullname = models.CharField(max_length=255, blank=True)
    
    language = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=255, blank=True)
    
    key = models.CharField(max_length=255)
    secret = models.CharField(max_length=255)
    
    user = models.ForeignKey(User, unique=True)
    
    
class DoubanAccount(models.Model):
    '''A douban account that linked with a django user'''
    # override default AutoField pk to force id to be assigned
    id = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=255)
    fullname = models.CharField(max_length=255)
    
    key = models.CharField(max_length=255)
    secret = models.CharField(max_length=255)
    
    user = models.ForeignKey(User, unique=True)    