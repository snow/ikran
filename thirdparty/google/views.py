#from django.views.generic import View
import logging

from django.views.generic import View
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login

from openid.consumer import consumer

from django_openid.models import DjangoOpenIDStore

from thirdparty.google.utils import get_openid_start_url, \
                                    exchange_access_token, GoogleBackend

#from thirdparty.models import *
_GOOGLE_OPENID_URI = 'https://www.google.com/accounts/o8/id'
_l = logging.getLogger(__name__)

class BaseV(View):
    '''Base class for all views that will use openid consumer'''
    _consumer = False
    _openidstore = False
        
    def get_openid_store(self):
        if not self._openidstore:
            self._openidstore = DjangoOpenIDStore()
        return self._openidstore
        
    def get_consumer(self, session):
        if not self._consumer:
            self._consumer = consumer.Consumer(session, self.get_openid_store())
        return self._consumer

        
class AuthStartV(BaseV):        
    '''
    start from here.
    
    callback MUST be provieded, either by subclassing or kwargs
    this view will build openid request and 
    redirect to google authorize page
    '''
    callback = False
    
    def get(self, request):
        if not self.callback:
            raise NotImplementedError('Subclass of AuthStartV must provide oauth_callback')
        
        c = self.get_consumer(request.session)
        trust_root = request.build_absolute_uri('/')
        callback = request.build_absolute_uri(self.callback)
        
        return HttpResponseRedirect(get_openid_start_url(c, trust_root,
                                                         callback))
    
class AuthReturnV(BaseV):        
    '''
    Google redirect user to here after authorize
    
    Subclass MUST override get() to provide actual business logic.
    DO call super get() first to make self.access_token available
    '''
    ax_resp = None
    access_token = None
    
    def get(self, request):
        c = self.get_consumer(request.session)
        resp = c.complete(request.GET, request.build_absolute_uri(request.path))
        
        if consumer.SUCCESS == resp.status:
            self.ax_resp = ax.FetchResponse.fromSuccessResponse(resp)
            oauth_resp = resp.extensionResponse(GoogleOAuthExt.ns_uri, True)
            
            if oauth_resp.request_token:
                self.access_token = exchange_access_token(
                                                    oauth_resp.request_token)
            else:
                raise Exception('request_token not found')
        else:
            pass # TODO openid failed
            
    
class AuthenticateReturnV(AuthReturnV):
    '''
    Return from Google authenticate
    '''
    def success(self, user):
        '''
        Called after authenticate success and logged user in.
        
        Subclass should override this method to provide actual business
        '''
        return HttpResponse('linked with {}'.format(user.username))
        
    def failed(self):
        '''
        Called after authenticate failed.
        
        Subclass should override this method to provide actual business
        '''
        return HttpResponse('authenticate failed')
    
    def get(self, request):
        '''
        Try to authenticate user with the google info
        '''
        # get self.access_token available
        super(AuthenticateReturnV, self).get(request)
        
        try:
            user = authenticate(cid=GoogleBackend.CID,
                                key=self.access_token.key, 
                                secret=self.access_token.secret,
                                email=self.ax_resp.email,
                                firstname=self.ax_resp.firstname,
                                lastname=self.ax_resp.lastname,
                                language=self.ax_resp.language,
                                country=self.ax_resp.country)
        except DuplicatedUsername:            
            raise # TODO
        else:
            if user:
                login(request, user)
                return self.success(user)
            else:
                return self.failed()