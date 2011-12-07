from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django_openid.registration import RegistrationConsumer
#from django_openid.consumer import SessionConsumer

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

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
    
    #(r'^openid/(.*)', RegistrationConsumer()),
    #(r'^openid/(.*)', SessionConsumer()),
)