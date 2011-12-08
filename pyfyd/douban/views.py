import logging

from django.views.generic import View
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.contrib.auth import authenticate, login

from client import OAuthClient
from oauth import OAuthToken 
from utils import DoubanBackend
from pyfyd.models import DuplicatedUsername

class BaseV(View):
    '''Base class for all views that will use douban oauth client'''
    def __init__(self, *args, **kwargs):
        super(BaseV, self).__init__(*args, **kwargs)
        
        self.client = OAuthClient(key=settings.DOUBAN_CONSUMER_KEY,
                                  secret=settings.DOUBAN_CONSUMER_SECRET)    
        
class AuthStartV(BaseV):        
    '''
    start from here.
    
    callback MUST be provieded, either by subclassing or kwargs
    this view will build openid request and 
    redirect to douban authorize page
    '''
    callback = False
    
    def get(self, request):
        if not self.callback:
            raise NotImplementedError('Subclass of AuthStartV must provide oauth_callback')
        
        req_token = OAuthToken(*self.client.get_request_token())
        request.session['req_token'] = req_token        
        callback = request.build_absolute_uri(self.callback)
        
        go_to = self.client.get_authorization_url(req_token.key, req_token.secret, 
                                                callback)        
        return HttpResponseRedirect(go_to)
    
class AuthReturnV(BaseV):        
    '''
    douban redirect user to here after authorize
    
    Subclass MUST override get() to provide actual business logic.
    DO call super get() first to make self.access_token available
    '''
    access_token = None
    uid = None
    
    def get(self, request):
        req_token = request.session.get('req_token', False)
        if req_token and req_token.key == request.GET['oauth_token']:        
            key, secret, uid = self.client.get_access_token(req_token.key, 
                                                            req_token.secret)
            if key and secret:
                self.access_token = OAuthToken(key, secret)
                self.uid = uid
            else:
                raise Exception('failed to get access token')
        else:
            raise Exception('where did u come from?')
            
    
class AuthenticateReturnV(AuthReturnV):
    '''
    Return from douban authenticate
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
        Try to authenticate user with the douban info
        '''
        # get self.access_token available
        super(AuthenticateReturnV, self).get(request)
        
        try:
            user = authenticate(cid=DoubanBackend.CID,
                                key=self.access_token.key, 
                                secret=self.access_token.secret,
                                uid=self.uid)
        except DuplicatedUsername:            
            # TODO
            raise 
        else:
            if user:
                login(request, user)
                return self.success(user)
            else:
                return self.failed()