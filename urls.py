from django.conf.urls.defaults import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

import django_pyrcp.thirdparty.twitter.views as twitter

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ikran.views.home', name='home'),
    # url(r'^ikran/', include('ikran.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include('api.urls')),
    
    url(r'^', include('webapp.urls')),
    
    url(r'^thirdparty/twitter/auth', twitter.AuthStartV.as_view()),
    url(r'^thirdparty/twitter/return', twitter.AuthReturnV.as_view()),
)