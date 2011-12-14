from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.decorators import login_required

from webapp.views import *
from webapp.thirdparty.views import *

urlpatterns = patterns('',
    url(r'^$', IndexV.as_view()),
    url(r'^dashboard/$', login_required(DashboardV.as_view())),
    
    #url(r'^people/(?P<username>.+)/$', 'notimplemented'),
    url(r'^people/(?P<username>.+)/recent/$', PeopleStreamV.as_view()),
    #url(r'^people/(?P<username>.+)/albums/(?P<pk>\d+)/(.*)', 'notimplemented'),
    #url(r'^people/(?P<username>.+)/tags/(?P<pk>\d+)/(.*)', 'notimplemented'),
    
    #url(r'^img/(?P<slug>.+)/', 'notimplemented'),
    #url(r'^img/(?P<slug>.+)/from/(?P<from>people)/(?P<username>.+)/', 'notimplemented'),
    #url(r'^img/(?P<slug>.+)/from/(?P<from>album)/(?P<album>\d+)/', 'notimplemented'),
    
    url(r'accounts/login/$', IndexV.as_view()),
    url(r'accounts/signin/$', IndexV.as_view()),

    url(r'thirdparty/douban/authenticate/$', DoubanAuthStartV.as_view()),
    url(r'thirdparty/douban/authenticate_return/$', 
        DoubanAuthenticateReturnV.as_view()),
                       
    url(r'thirdparty/google/authenticate/$', GoogleAuthStartV.as_view()),
    url(r'thirdparty/google/authenticate_return/$', 
        GoogleAuthenticateReturnV.as_view()),
                       
    url(r'thirdparty/twitter/authenticate/$', TwitterAuthStartV.as_view()),
    url(r'thirdparty/twitter/authenticate_return/$', 
        TwitterAuthenticateReturnV.as_view()),
    
    url(r'under_construction/$', UnderConstructionV.as_view()),
)