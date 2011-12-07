#from django.views.generic import View
from django.views.generic import View
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from tweepy import OAuthHandler, API

from thirdparty.models import TwitterAccount

BASE_URI = settings.PYRCP_THIRDPARTYSERVICE_URI_ROOT + '/twitter'
AUTHORIZE_START_URI = BASE_URI + '/authorize/'
AUTHORIZE_RETURN_URI = BASE_URI + '/authorize_return/'
AUTHORIZE_DONE_URI = BASE_URI + '/authorize_done/'

class BaseOAuthV(View):
    '''Base class for all views that will use OAuth handler'''
    def __init__(self, *args, **kwargs):
        self.oauth = OAuthHandler(settings.TWITTER_CONSUMER_KEY,
                                  settings.TWITTER_CONSUMER_SECRET,
                                  secure=True)
        super(BaseOAuthV, self).__init__(*args, **kwargs)
    
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
        
class AuthStartV(BaseOAuthV):        
    '''Start from here. Redirect to twitter authorizing page'''    
    def get(self, request, signin_with_twitter=True):
        self.oauth.callback = request.build_absolute_uri(AUTHORIZE_RETURN_URI)
        #redirect_to = self.oauth.get_authorization_url()
        redirect_to = self.oauth.get_authorization_url(signin_with_twitter)
        # request token could only being get after get_authorization_url()
        request.session['unauthed_token'] = self.oauth.request_token
        return HttpResponseRedirect(redirect_to)
    
class AuthReturnV(BaseOAuthV):        
    '''Twitter redirect user to here after authorize'''    
    def get(self, request):
        if request.session['unauthed_token'].key == request.GET['oauth_token']:
            self.oauth.set_request_token(request.GET['oauth_token'], 
                                         settings.TWITTER_CONSUMER_SECRET)
            access_token = self.oauth.get_access_token(
                                request.GET['oauth_verifier'])
        else:
            raise Exception('token not match, something went wrong')
        
        tweepy_user = API(auth_handler=self.oauth).verify_credentials()
        
        
        return HttpResponse('connected with {} {}'.\
                                format(tweepy_user.id, 
                                       tweepy_user.screen_name))
        #return HttpResponseRedirect(AUTHORIZE_DONE_URI)
    
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
        