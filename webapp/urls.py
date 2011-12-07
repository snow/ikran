from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.decorators import login_required

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

from webapp.views import *

urlpatterns = patterns('',
    url(r'^$', IndexV.as_view()),
    url(r'^dashboard/$', login_required(DashboardV.as_view())),
    
    url(r'^thirdparty/', include('webapp.thirdparty.urls')),
)