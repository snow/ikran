#from django.views.generic import View
from django.views.generic import View
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login
from tweepy import OAuthHandler, API

from thirdparty.models import *

class BaseOAuthV(View):
    '''Base class for all views that will use OAuth handler'''
    def __init__(self, *args, **kwargs):
        self.oauth = OAuthHandler(settings.TWITTER_CONSUMER_KEY,
                                  settings.TWITTER_CONSUMER_SECRET,
                                  secure=True)
        super(BaseOAuthV, self).__init__(*args, **kwargs)

        
class AuthStartV(BaseOAuthV):        
    '''
    OAuth start from here.
    
    oauth_callback MUST be provieded, either by subclassing or kwargs
    this view will build oauth request and 
    redirect to twitter authorize or auchenticate page
    '''
    oauth_callback = False
    signin_with_twitter = False
    
    def get(self, request, signin_with_twitter=True):
        if not self.oauth_callback:
            raise Exception('Subclass of AuthStartV must provide oauth_callback')
        
        self.oauth.callback = request.build_absolute_uri(self.oauth_callback)
        #redirect_to = self.oauth.get_authorization_url()
        redirect_to = self.oauth.get_authorization_url(self.signin_with_twitter)
        # request token could only being get after get_authorization_url()
        request.session['unauthed_token'] = self.oauth.request_token
        return HttpResponseRedirect(redirect_to)
    
class AuthReturnV(BaseOAuthV):        
    '''
    Twitter redirect user to here after authorize
    
    Subclass MUST override get() to provide actual business logic.
    DO call super get() first to make self.access_token available
    '''
    access_token = None
    
    def get(self, request):
        if request.session['unauthed_token'].key == request.GET['oauth_token']:
            self.oauth.set_request_token(request.GET['oauth_token'], 
                                         settings.TWITTER_CONSUMER_SECRET)
            # give a oauth.OAuthToken object to override
            self.access_token = self.oauth.get_access_token(
                                    request.GET['oauth_verifier'])
        else:
            raise Exception('token not match, something went wrong')
        
        # give a tweepy.models.User object to override
        # self.twitter_user = API(auth_handler=self.oauth).verify_credentials()
        
        
class AuthenticateReturnV(AuthReturnV):
    '''TODO'''
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
        # get self.access_token available
        super(AuthenticateReturnV, self).get(request)
        
        try:
            user = authenticate(cid=TwitterBackend.CID,
                                key=self.access_token.key, 
                                secret=self.access_token.secret)
        except DuplicatedUsername:            
            pass # TODO
        else:
            if user:
                login(request, user)
                
                return self.success(user)
            else:
                return self.failed()
#        return HttpResponse('connected with {} {}'.\
#                                format(tweepy_user.id, 
#                                       tweepy_user.screen_name))
        #return HttpResponseRedirect(AUTHORIZE_DONE_URI)
        
#class IndexV(BaseOAuthV):    
#    '''Index, determine what action should take'''
#    def get(self, request):
#        if request.user.is_authenticated():        
#            profile = request.user.get_profile()
#            
#            if profile.is_twitter_linked():
#                return HttpResponseRedirect(AUTHORIZE_DONE_URI)
#            else:
#                return HttpResponseRedirect(AUTHORIZE_START_URI)
#        else:
#            # show signin with twitter page
#            pass

#class AuthDoneV(BaseOAuthV):
#    '''TODO'''
#    def get(self, request):
#        up = request.user.get_profile()
#        
#        self.oauth.set_access_token(up.get_twitter_token())
#        twittter_user = API(auth_handler=self.oauth).verify_credentials()
#        
#        return HttpResponse('connected with {} {}'.\
#                                format(twittter_user.id, 
#                                       twittter_user.screen_name))
    
#class AuthenticateV(BaseOAuthV):        
#    '''View for path/to/3rdparty/twitter/authenticate'''
#    def get(self, request):        
#        pass
    
#class SignoutV(BaseOAuthV):
#    '''/to/thirdparty/twitter/signout/'''
#    def get(self, request, *args, **kwargs):
#        request.session.flush()
#        return HttpResponseRedirect('/')
        