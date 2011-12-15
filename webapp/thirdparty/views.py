# Create your views here.
#from django.views.generic import View, TemplateView, DetailView, RedirectView
#from django.contrib.auth.models import User
#import thirdparty.twitter.views as ttv
#from thirdparty.models import TwitterAccount
#from django.http import HttpResponse, HttpResponseRedirect

import pyfyd.google.views as pgv
import pyfyd.twitter.views as ptv
import pyfyd.douban.views as pdv

class DoubanAuthStartV(pdv.AuthStartV):
    '''Mixin handles every thing'''    
    callback = '/thirdparty/douban/authenticate_return/'
    
class DoubanAuthenticateReturnV(pdv.AuthenticateReturnV):
    '''Mixin handles every thing'''
    success_uri = '/dashboard/'
    
class GoogleAuthStartV(pgv.AuthStartV):
    '''Mixin handles every thing'''
    callback = '/thirdparty/google/authenticate_return/'    
    
class GoogleAuthenticateReturnV(pgv.AuthenticateReturnV):
    '''Mixin handles every thing'''
    success_uri = '/dashboard/'
    
class TwitterAuthStartV(ptv.AuthStartV):
    '''Mixin handles every thing'''    
    callback = '/thirdparty/twitter/authenticate_return/'
    
class TwitterAuthenticateReturnV(ptv.AuthenticateReturnV):
    '''Mixin handles every thing'''
    success_uri = '/dashboard/'