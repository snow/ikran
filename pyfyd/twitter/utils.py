from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend
from django.conf import settings
from tweepy import OAuthHandler, API
from pyfyd.models import TwitterAccount, DuplicatedUsername

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
            account = TwitterAccount.objects.\
                            filter(id=twitter_user.id).get()
            
        except TwitterAccount.DoesNotExist:
            account = TwitterAccount(id=twitter_user.id, 
                                     username=twitter_user.screen_name,
                                     fullname=twitter_user.name,
                                     key=key,
                                     secret=secret)
            
            if User.objects.filter(username=account.username).exists():
                raise DuplicatedUsername(account.username)
            else:
                user = User.objects.create_user(account.username, 
                                                '{}@n.cc'.\
                                                    format(account.username))
                account.user = user
                account.save()
        else:
            updated = False      
            # update key and secret if changed                            
            if account.key != key:
                account.key = key
                account.secret = secret
                updated = True
            
            if account.username != twitter_user.screen_name:
                account.username = twitter_user.screen_name
                updated = True
                
            if account.fullname != twitter_user.name:
                account.fullname = twitter_user.name
                updated = True
            
            if updated:
                account.save()
        
        return account.user