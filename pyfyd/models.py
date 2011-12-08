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

class TwitterBackend(ModelBackend):
    '''Twitter auth backend'''
    CID = 'pyfyd.models.TwitterBackend'
    
    def authenticate(self, cid, key, secret):
        if self.CID != cid:
            return None
        
        oauth = OAuthHandler(settings.TWITTER_CONSUMER_KEY,
                             settings.TWITTER_CONSUMER_SECRET,
                             secure=True)
        oauth.set_access_token(key, secret)
        twitter_user = API(auth_handler=oauth).verify_credentials()
        
        if not twitter_user:
            return None
        
        try:
            taccount = TwitterAccount.objects.\
                            filter(id=twitter_user.id).get()
                            
            # update key and secret if changed                            
            if taccount.key != key:
                taccount.key = key
                taccount.secret = secret
                taccount.save()
            
            # update username if changed    
            if taccount.username != twitter_user.screen_name:
                taccount.username = twitter_user.screen_name
                taccount.save()
                
            return taccount.user
        except TwitterAccount.DoesNotExist:
            taccount = TwitterAccount(id=twitter_user.id, 
                                      username=twitter_user.screen_name,
                                      key=key,
                                      secret=secret)
            
            if User.objects.filter(username=taccount.username).exists():
                raise DuplicatedUsername(taccount.username)
            else:
                user = User.objects.create_user(taccount.username, 
                                                '{}@n.cc'.\
                                                    format(taccount.username))
                taccount.user = user
                taccount.save()
                return user
            
class GoogleAccount(models.Model):
    '''A google account that linked with a django user'''
    username = models.CharField(max_length=255)
    fullname = models.CharField(max_length=255, blank=True)
    language = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=255, blank=True)
    
    key = models.CharField(max_length=255)
    secret = models.CharField(max_length=255)
    
    user = models.ForeignKey(User, unique=True)