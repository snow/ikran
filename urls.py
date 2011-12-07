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
    
    #(r'^openid/(.*)', RegistrationConsumer()),
    #(r'^openid/(.*)', SessionConsumer()),
)

import thirdparty.twitter.views as ttv
#import webapps.thirdparty.twitter.views as wttv

urlpatterns += patterns('',
    url(r'^thirdparty/twitter/authenticate/', 
        ttv.AuthStartV.as_view(
            # TODO: is there any way to dymically determin 
            # the "/thirdparty/" part?
            oauth_callback='/thirdparty/twitter/authenticate_return/', 
            signin_with_twitter=True)
    ),
    url(r'^thirdparty/twitter/authorize/', 
        ttv.AuthStartV.as_view(
            oauth_callback='/thirdparty/twitter/authorize_return/', 
            signin_with_twitter=False)
    ),
    url(r'^thirdparty/twitter/authenticate_return/', 
        ttv.AuthenticateReturnV.as_view()),
)

import thirdparty.google.views as tgv

urlpatterns += patterns('',
    url(r'thirdparty/google/authenticate/', 
        tgv.AuthStartV.as_view(
            callback='/thirdparty/google/authenticate_return/')
    ),
    url(r'thirdparty/google/authenticate_return/', 
        tgv.AuthenticateReturnV.as_view()),
)