from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

from api.img.views import *

urlpatterns = patterns('api.views',
    url(r'^upload.(?P<format>json|html)', ''),
    #url(r'^gruburi.(?P<format>json|html)', ''),
)