import logging
import urlparse
import time
from urllib2 import Request, urlopen, HTTPError

from tweepy import oauth
from openid import extension
from openid.extensions import ax
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend

from pyfyd.models import GoogleAccount, DuplicatedUsername

AX_NS_EMAIL = 'http://axschema.org/contact/email'
AX_NS_FIRSTNAME = 'http://axschema.org/namePerson/first'
AX_NS_LASTNAME = 'http://axschema.org/namePerson/last'
AX_NS_LANGUAGE = 'http://axschema.org/pref/language'
AX_NS_COUNTRY = 'http://axschema.org/contact/country/home'

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
    ax_request.add(ax.AttrInfo(AX_NS_EMAIL, required=True))
    ax_request.add(ax.AttrInfo(AX_NS_FIRSTNAME))
    ax_request.add(ax.AttrInfo(AX_NS_LASTNAME))
    ax_request.add(ax.AttrInfo(AX_NS_LANGUAGE))
    ax_request.add(ax.AttrInfo(AX_NS_COUNTRY))
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
    request_token = oauth.OAuthToken(request_token, '')
                
    request = oauth.OAuthRequest.\
                from_consumer_and_token(consumer,
                                        token=request_token, 
                                        http_url=_GOOGLE_ACCESS_TOKEN_URI)    
    request.sign_request(sigmethod, consumer, request_token)
    headers = request.to_header()
    
    resp = urlopen(Request(_GOOGLE_ACCESS_TOKEN_URI, headers=headers))
    return oauth.OAuthToken.from_string(resp.read())

def parse_hybrid_response(resp):
    '''
    Extract attribute exchange results and request token from openid response
    
    @return:  
    * user_attrs openid.extensions.ax.FetchResponse
    * access_token oauth.OAuthToken
    '''
    user_attrs = ax.FetchResponse.fromSuccessResponse(resp)
    oauth_resp = resp.extensionResponse(GoogleOAuthExt.ns_uri, True)
    
    try:
        request_token = oauth_resp['request_token']
    except KeyError:
        raise Exception('request_token not found')
    else:
        access_token = exchange_access_token(request_token)
        
        if not access_token:
            raise Exception('failed to get access token')
        
        return user_attrs, access_token

class GoogleBackend(ModelBackend):
    '''Google auth backend'''
    CID = 'pyfyd.google.utils.GoogleBackend'
    
    def authenticate(self, cid, key, secret, user_attrs):
        if self.CID != cid:
            return None
              
        email=user_attrs.getSingle(AX_NS_EMAIL)
        language=user_attrs.getSingle(AX_NS_LANGUAGE, '')
        country=user_attrs.getSingle(AX_NS_COUNTRY, '')
        
        username = email.split('@')[0]
        fullname = '{} {}'.format(user_attrs.getSingle(AX_NS_FIRSTNAME, ''), 
                                  user_attrs.getSingle(AX_NS_LASTNAME, '')).\
                            strip()
        try:
            account = GoogleAccount.objects.filter(username=username).get()
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
        else:
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