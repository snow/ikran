import json

from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend
from django.conf import settings

from pyfyd.models import DoubanAccount, DuplicatedUsername
from client import OAuthClient
from oauth import escape

_PROFILE_URI_BASE = 'http://api.douban.com/people/{}?alt=json'

class DoubanBackend(ModelBackend):
    '''Douban auth backend'''
    CID = 'pyfyd.douban.utils.DoubanBackend'
    
    def authenticate(self, cid, key, secret, uid):
        if self.CID != cid:
            return None
        import logging
        l = logging.getLogger('c')
        
        client = OAuthClient(key=settings.DOUBAN_CONSUMER_KEY,
                             secret=settings.DOUBAN_CONSUMER_SECRET)
        client.login(key, secret)
        
        resp = client.access_resource('GET', _PROFILE_URI_BASE.format(uid))
        try:
            douban_user = json.loads(resp.read())
        except:
            return None
    
        id = douban_user['uri']['$t'].split('/')[-1]
        username = douban_user['db:uid']['$t']
        fullname = douban_user['title']['$t']
        
        try:
            account = DoubanAccount.objects.filter(id=id).get()            
        except DoubanAccount.DoesNotExist:
            account = DoubanAccount(id=id, 
                                    username=username,
                                    fullname=fullname,
                                    key=key,
                                    secret=secret)
            
            if User.objects.filter(username=username).exists():
                raise DuplicatedUsername(username)
            else:
                user = User.objects.create_user(username, 
                                                '{}@n.cc'.format(username))
                account.user = user
                account.save()
        else:
            updated = False      
            # update key and secret if changed                            
            if account.key != key:
                account.key = key
                account.secret = secret
                updated = True
            
            if account.username != username:
                account.username = username
                updated = True
                
            if account.fullname != fullname:
                account.fullname = fullname
                updated = True
            
            if updated:
                account.save()
        
        return account.user