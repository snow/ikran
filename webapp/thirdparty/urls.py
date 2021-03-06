from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.decorators import login_required

from webapp.thirdparty.views import *

urlpatterns = patterns('',    
    url(r'^$', IndexV.as_view()),
    
    url(r'^douban/authenticate/$', DoubanAuthenticateStartV.as_view()),
    url(r'^douban/authenticate_return/$', DoubanAuthenticateReturnV.as_view()),
    url(r'^douban/authorize/$', DoubanAuthorizeStartV.as_view()),
    url(r'^douban/authorize_return/$', DoubanAuthorizeReturnV.as_view()),
    url(r'^douban/', include('webapp.thirdparty.douban.urls')),
                       
    url(r'^google/authenticate/$', GoogleAuthenticateStartV.as_view()),
    url(r'^google/authenticate_return/$', GoogleAuthenticateReturnV.as_view()),
    url(r'^google/authorize/$', GoogleAuthorizeStartV.as_view()),
    url(r'^google/authorize_return/$', GoogleAuthorizeReturnV.as_view()),
                       
    url(r'^twitter/authenticate/$', TwitterAuthenticateStartV.as_view()),
    url(r'^twitter/authenticate_return/$', TwitterAuthenticateReturnV.as_view()),
    url(r'^twitter/authorize/$', TwitterAuthorizeStartV.as_view()),
    url(r'^twitter/authorize_return/$', TwitterAuthorizeReturnV.as_view()),
    
    url(r'^flickr/authorize/$', FlickrAuthorizeStartV.as_view()),
    url(r'^flickr/authorize_return/$', FlickrAuthorizeReturnV.as_view()),
)