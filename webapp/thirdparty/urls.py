from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.decorators import login_required

import thirdparty.twitter.views as ttv
import thirdparty.google.views as tgv
#import webapps.thirdparty.twitter.views as wttv

urlpatterns = patterns('',
    #url(r'^$', IndexV.as_view()),
    
    #url(r'^twitter/$', login_required(DashboardV.as_view())),    
    url(r'^twitter/authenticate/', 
        ttv.AuthStartV.as_view(
            # TODO: is there any way to dymically determin 
            # the "/thirdparty/" part?
            oauth_callback='/thirdparty/twitter/authenticate_return/', 
            signin_with_twitter=True)
    ),
    url(r'^twitter/authorize/', 
        ttv.AuthStartV.as_view(
            oauth_callback='/thirdparty/twitter/authorize_return/', 
            signin_with_twitter=False)
    ),
    url(r'^twitter/authenticate_return/', ttv.AuthenticateReturnV.as_view()),
    #url(r'^twitter/authorize_return/', wttv.AuthorizeReturnV.as_view()),
    
    url(r'google/auth/', 
        tgv.AuthStartV.as_view(callback='/thirdparty/google/return/')),
    url(r'google/return/', tgv.AuthReturnV.as_view()),
)