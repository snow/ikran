import logging
from urllib2 import Request, urlopen, HTTPError

from tweepy import oauth

from openid import extension
from openid.extensions import ax

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend

from thirdparty.models import DuplicatedUsername

_l = logging.getLogger(__name__)

class GoogleOAuthExt(extension.Extension):
    ns_uri = 'http://specs.openid.net/extensions/oauth/1.0'
    ns_alias = 'oauth'
    _scopes = False
    
    def __init__(self):
        # at least one scope is required
        # or google will ignore oauth extension
        self._scopes = ['https://www.googleapis.com/auth/plus.me']
    
    def add_scope(self, scope):
        '''Add a Google service to request access'''
        if scope not in self._scopes:
            self._scopes.append(scope)
    
    def getExtensionArgs(self):
        return {
            'consumer': settings.GOOGLE_CONSUMER_KEY,
            'scope': '+'.join(self._scopes),
        }

_GOOGLE_OPENID_URI = 'https://www.google.com/accounts/o8/id'        
def get_openid_start_url(consumer, trust_root, callback):
    '''build openid request and return as string'''
    auth_request = consumer.begin(_GOOGLE_OPENID_URI)
        
    ax_request = ax.FetchRequest()
    ax_request.add(ax.AttrInfo('http://axschema.org/contact/email',
                               required=True))
    ax_request.add(ax.AttrInfo('http://axschema.org/namePerson/first'))
    ax_request.add(ax.AttrInfo('http://axschema.org/namePerson/last'))
    ax_request.add(ax.AttrInfo('http://axschema.org/pref/language'))
    ax_request.add(ax.AttrInfo('http://axschema.org/contact/country/home'))
    auth_request.addExtension(ax_request)
    
    auth_request.addExtension(GoogleOAuthExt())
    
    go_to = auth_request.redirectURL(trust_root, callback)
    
    return go_to
         
_GOOGLE_ACCESS_TOKEN_URI = 'https://www.google.com/accounts/OAuthGetAccessToken'         
def exchange_access_token(request_token):
    '''Exchange request token for access token'''
    consumer = oauth.OAuthConsumer(settings.GOOGLE_CONSUMER_KEY,
                                   settings.GOOGLE_CONSUMER_SECRET)
    sigmethod = oauth.OAuthSignatureMethod_HMAC_SHA1()
    request_token = oauth.OAuthToken(request_token, 
                                     settings.GOOGLE_CONSUMER_SECRET)
                
    request = oauth.OAuthRequest.\
                from_consumer_and_token(consumer,
                                        token=request_token, 
                                        http_url=_GOOGLE_ACCESS_TOKEN_URI)
    #request.set_parameter('oauth_verifier', '')
    request.sign_request(sigmethod, consumer, request_token)

    # send request
    headers = request.to_header()
    try:
        resp = urlopen(Request(_GOOGLE_ACCESS_TOKEN_URI, headers=headers))
    except HTTPError as err:
        _l.debug(err.fp.read())
        raise
    else:        
        return oauth.OAuthToken.from_string(resp.read())

class GoogleBackend(ModelBackend):
    '''Google auth backend'''
    CID = 'thirdparty.google.utils.GoogleBackend'
    
    def authenticate(self, cid, email, key, secret, firstname='', lastname='', 
                     language='', country=''):
        if self.CID != cid:
            return None
        
        username = email.split('@')[0]
        fullname = '{} {}'.format(firstname, lastname).strip()
        
        try:
            account = GoogleAccount.objects.filter(username=username).get()
            
            updated = False
            # update key and secret if changed                            
            if account.key != key:
                account.key = key
                account.secret = secret
                updated = True
                
            if account.fullname != fullname:
                account.fullname = fullname
                updated = True
                
            if account.language != language:
                account.language = language
                updated = True
                
            if account.country != country:
                account.country = country
                updated = True
            
            if updated:
                account.save()
            
            return account.user
        
        except GoogleAccount.DoesNotExist:
            account = GoogleAccount(username=username,
                                    key=key,
                                    secret=secret,
                                    fullname=fullname,
                                    language=language,
                                    country=country)
            
            if User.objects.filter(username=username).exists():
                raise DuplicatedUsername(username)
            else:
                user = User.objects.create_user(username, email)
                account.user = user
                account.save()
                return user