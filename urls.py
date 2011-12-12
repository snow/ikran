from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django_openid.registration import RegistrationConsumer
#from django_openid.consumer import SessionConsumer

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include('api.urls')),
    
    url(r'^', include('webapp.urls')),
    
    url(r'^accounts/signout/$', 'django.contrib.auth.views.logout', 
        {'next_page': '/'}),
    
    #(r'^openid/(.*)', RegistrationConsumer()),
    #(r'^openid/(.*)', SessionConsumer()),
)

import pyfyd.twitter.views as ptv
#import webapps.thirdparty.twitter.views as wttv

urlpatterns += patterns('',
    url(r'^thirdparty/twitter/authenticate/', 
        ptv.AuthStartV.as_view(
            # TODO: is there any way to dymically determin 
            # the "/thirdparty/" part?
            callback='/thirdparty/twitter/authenticate_return/', 
            signin=True)
    ),
    url(r'^thirdparty/twitter/authorize/', 
        ptv.AuthStartV.as_view(
            callback='/thirdparty/twitter/authorize_return/', 
            signin=False)
    ),
    url(r'^thirdparty/twitter/authenticate_return/', 
        ptv.AuthenticateReturnV.as_view(success_uri='/dashboard/')),
)

import pyfyd.google.views as pgv

urlpatterns += patterns('',
    url(r'thirdparty/google/authenticate/', 
        pgv.AuthStartV.as_view(
            callback='/thirdparty/google/authenticate_return/')
    ),
    url(r'thirdparty/google/authenticate_return/', 
        pgv.AuthenticateReturnV.as_view(success_uri='/dashboard/')),
)

import pyfyd.douban.views as pdv

urlpatterns += patterns('',
    url(r'thirdparty/douban/authenticate/', 
        pdv.AuthStartV.as_view(
            callback='/thirdparty/douban/authenticate_return/')
    ),
    url(r'thirdparty/douban/authenticate_return/', 
        pdv.AuthenticateReturnV.as_view(success_uri='/dashboard/')),
)