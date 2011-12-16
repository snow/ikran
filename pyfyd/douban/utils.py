import json

from django.conf import settings

from pyfyd.models import DoubanAccount
from pyfyd.common.utils import BaseBackend
from client import OAuthClient 

_PROFILE_URI_BASE = 'http://api.douban.com/people/{}?alt=json'
class DoubanBackend(BaseBackend):
    '''Douban auth backend'''
    CID = 'pyfyd.douban.utils.DoubanBackend'
    account_cls = DoubanAccount
    attribute_keys = ['key', 'secret', 'username', 'fullname']
    
    @classmethod
    def get_account_from_token(cls, key, secret, uid):
        client = OAuthClient(key=settings.DOUBAN_CONSUMER_KEY,
                             secret=settings.DOUBAN_CONSUMER_SECRET)
        client.login(key, secret)
        
        resp = client.access_resource('GET', _PROFILE_URI_BASE.format(uid))
        resp = json.loads(resp.read())
        
        id = resp['uri']['$t'].split('/')[-1]
        username = resp['db:uid']['$t']
        fullname = resp['title']['$t']
        
        return DoubanAccount(id=id, 
                             username=username,
                             key=key,
                             secret=secret,
                             fullname=fullname)    
    
#    def authenticate(self, cid, key, secret, uid):
#        if self.CID != cid:
#            return None
#
#        account = get_account_from_token(key, secret, uid)
#        qs = DoubanAccount.objects.filter(id=account.id)
#        
#        if qs.exists():
#            account = update_account(qs.get(), account)
#        else:
#            if User.objects.filter(username=account.username).exists():
#                raise DuplicatedUsername(account.username)
#            else:
#                user = User.objects.create_user(account.username)
#                account.user = user
#                account.save()
#                
#        return account.user
        
#        try:
#            exist = DoubanAccount.objects.filter(id=account.id).get()            
#        except DoubanAccount.DoesNotExist:
#            if User.objects.filter(username=account.username).exists():
#                raise DuplicatedUsername(account.username)
#            else:
#                user = User.objects.create_user(username, 
#                                                '{}@douban.com'.\
#                                                    format(account.username))
#                account.user = user
#                account.save()
#        else:
#            self.update_account(exist, account)
#                
#            user = exist.user
#        
#        return user
#    
#    