# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
import django.views.generic as gv

from pyfyd.models import TwitterAccount, GoogleAccount, DoubanAccount
import pyfyd.google.views as pgv
import pyfyd.twitter.views as ptv
import pyfyd.douban.views as pdv

class IndexV(gv.TemplateView):
    template_name = 'webapp/thirdparty.html'
    
    def get_context_data(self, *args, **kwargs):
        context = super(IndexV, self).get_context_data(*args, **kwargs)
        
        try:
            context['douban_account'] = DoubanAccount.objects.\
                                            filter(user=self.request.user).get()
        except DoubanAccount.DoesNotExist:
            context['douban_account'] = False
            
        try:
            context['google_account'] = GoogleAccount.objects.\
                                            filter(user=self.request.user).get()
        except GoogleAccount.DoesNotExist:
            context['google_account'] = False
            
        try:
            context['twitter_account'] = TwitterAccount.objects.\
                                            filter(user=self.request.user).get()
        except TwitterAccount.DoesNotExist:
            context['twitter_account'] = False
            
        return context


class DoubanAuthenticateStartV(pdv.AuthStartV):
    '''super handles every thing'''    
    callback = '/thirdparty/douban/authenticate_return/'
    
class DoubanAuthenticateReturnV(pdv.AuthenticateReturnV):
    '''super handles every thing'''
    success_uri = '/dashboard/'
    
class DoubanAuthorizeStartV(pdv.AuthStartV):
    '''super handles every thing'''    
    callback = '/thirdparty/douban/authorize_return/'
    
class DoubanAuthorizeReturnV(pdv.AuthorizeReturnV):
    '''super handles every thing'''
    success_uri = '/thirdparty/'
    
    def get(self, request, *args, **kwargs):
        super(DoubanAuthorizeReturnV, self).get(request, *args, **kwargs)
        
        return HttpResponseRedirect(self.success_uri)    
    
    
class GoogleAuthenticateStartV(pgv.AuthStartV):
    '''super handles every thing'''
    callback = '/thirdparty/google/authenticate_return/'
    
class GoogleAuthenticateReturnV(pgv.AuthenticateReturnV):
    '''super handles every thing'''
    success_uri = '/dashboard/'
    
class GoogleAuthorizeStartV(pgv.AuthStartV):
    '''super handles every thing'''
    callback = '/thirdparty/google/authorize_return/'
    
class GoogleAuthorizeReturnV(pgv.AuthorizeReturnV):
    '''super handles every thing'''
    success_uri = '/thirdparty/'    
    
    def get(self, request, *args, **kwargs):
        super(GoogleAuthorizeReturnV, self).get(request, *args, **kwargs)
        
        return HttpResponseRedirect(self.success_uri)    
    
    
class TwitterAuthenticateStartV(ptv.AuthStartV):
    '''super handles every thing'''    
    callback = '/thirdparty/twitter/authenticate_return/'
    signin = True
    
class TwitterAuthenticateReturnV(ptv.AuthenticateReturnV):
    '''super handles every thing'''
    success_uri = '/dashboard/'
    
class TwitterAuthorizeStartV(ptv.AuthStartV):
    '''super handles every thing'''    
    callback = '/thirdparty/twitter/authorize_return/'
    signin = False
    
class TwitterAuthorizeReturnV(ptv.AuthorizeReturnV):
    '''super handles every thing'''
    success_uri = '/thirdparty/'    
    
    def get(self, request, *args, **kwargs):
        super(TwitterAuthorizeReturnV, self).get(request, *args, **kwargs)
        
        return HttpResponseRedirect(self.success_uri)    