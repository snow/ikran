#from django.views.generic import View
import logging

from django.views.generic import View
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login

from openid.consumer import consumer
from openid.extensions import ax
from openid.server.trustroot import RP_RETURN_TO_URL_TYPE

from django_openid.models import DjangoOpenIDStore

from thirdparty.models import GoogleOAuthExt

#from thirdparty.models import *
_GOOGLE_OPENID_URI = 'https://www.google.com/accounts/o8/id'
_l = logging.getLogger(__name__)

class BaseOAuthV(View):
    '''Base class for all views that will use OAuth handler'''
    _consumer = False
    _openidstore = False
    
    def __init__(self, *args, **kwargs):
#        self.oauth = OAuthHandler(settings.TWITTER_CONSUMER_KEY,
#                                  settings.TWITTER_CONSUMER_SECRET,
#                                  secure=True)
        
        super(BaseOAuthV, self).__init__(*args, **kwargs)
        
    def get_openid_store(self):
        if not self._openidstore:
            self._openidstore = DjangoOpenIDStore()
        return self._openidstore
        
    def get_consumer(self, session):
        if not self._consumer:
            self._consumer = consumer.Consumer(session, 
                                               self.get_openid_store())
        return self._consumer

        
class AuthStartV(BaseOAuthV):        
    '''
    OAuth start from here.
    
    oauth_callback MUST be provieded, either by subclassing or kwargs
    this view will build oauth request and 
    redirect to twitter authorize or auchenticate page
    '''
    callback = False
    is_signin = False
    
    def get(self, request):
        if not self.callback:
            raise NotImplementedError('Subclass of AuthStartV must provide oauth_callback')
        
        c = self.get_consumer(request.session)
        
        auth_request = c.begin(_GOOGLE_OPENID_URI)
        
        ax_request = ax.FetchRequest()
        ax_request.add(ax.AttrInfo('http://axschema.org/contact/email',
                                   required=True))
        #auth_request.addExtension(ax_request)
        
        auth_request.addExtension(GoogleOAuthExt())
        
        trust_root = request.build_absolute_uri('/')
        callback = request.build_absolute_uri(self.callback)
        go_to = auth_request.redirectURL(trust_root, callback)
        
        #_l.info(go_to)
        
        return HttpResponseRedirect(go_to)
        
#        self.oauth.callback = request.build_absolute_uri(self.oauth_callback)
#        #redirect_to = self.oauth.get_authorization_url()
#        redirect_to = self.oauth.get_authorization_url(self.signin_with_twitter)
#        # request token could only being get after get_authorization_url()
#        request.session['unauthed_token'] = self.oauth.request_token
#        return HttpResponseRedirect(redirect_to)
    
class AuthReturnV(BaseOAuthV):        
    '''
    Twitter redirect user to here after authorize
    
    Subclass MUST override get() to provide actual business logic.
    DO call super get() first to make self.access_token available
    '''
    #access_token = None
    
    def get(self, request):
        c = self.get_consumer(request.session)
        resp = c.complete(request.GET, request.build_absolute_uri(request.path))
        
        if consumer.SUCCESS == resp.status:
            ax_response = ax.FetchResponse.fromSuccessResponse(resp)
            #_l.info(resp)
            #_l.info(resp.message)
            #_l.info(ax_response)
            #_l.info(resp.extensionResponse(GoogleOAuthExt.ns_uri, True))
            
        else:
            pass
            #_l.info(resp.status)
        
        return HttpResponse(resp.extensionResponse(GoogleOAuthExt.ns_uri, True)) 
        
#        if request.session['unauthed_token'].key == request.GET['oauth_token']:
#            self.oauth.set_request_token(request.GET['oauth_token'], 
#                                         settings.TWITTER_CONSUMER_SECRET)
#            # give a oauth.OAuthToken object to override
#            self.access_token = self.oauth.get_access_token(
#                                    request.GET['oauth_verifier'])
#        else:
#            raise Exception('token not match, something went wrong')
        
        # give a tweepy.models.User object to override
        # self.twitter_user = API(auth_handler=self.oauth).verify_credentials()
        
 