from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.decorators import login_required

from webapp.views import *

urlpatterns = patterns('',
    url(r'^i/(?P<slug>.+)/(?P<format>.*)/?$', ImageV.as_view()),                    
                       
    url(r'^$', IndexV.as_view()),
    url(r'^dashboard/$', login_required(DashboardV.as_view())),
    
    url(r'^people/(?P<username>.+)/$', PeopleStreamV.as_view()),
    url(r'^people/(?P<username>.+)/recent/$', PeopleStreamV.as_view()),
    #url(r'^people/(?P<username>.+)/albums/(?P<pk>\d+)/(.*)', 'notimplemented'),
    #url(r'^people/(?P<username>.+)/tags/(?P<pk>\d+)/(.*)', 'notimplemented'),
    
    #url(r'^img/(?P<slug>.+)/', 'notimplemented'),
    #url(r'^img/(?P<slug>.+)/from/(?P<from>people)/(?P<username>.+)/', 'notimplemented'),
    #url(r'^img/(?P<slug>.+)/from/(?P<from>album)/(?P<album>\d+)/', 'notimplemented'),
    
    url(r'^album/(?P<pk>\d+)/', AlbumV.as_view()),
    
    url(r'^public/', PublicStreamV.as_view()),
    
    url(r'accounts/login/$', IndexV.as_view()),
    url(r'accounts/signin/$', IndexV.as_view()),
    url(r'accounts/settings/$', SettingsV.as_view()),
    
    url(r'thirdparty/', include('webapp.thirdparty.urls')),
    
    url(r'under_construction/$', UnderConstructionV.as_view()),
)