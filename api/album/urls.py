from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.decorators import login_required

from api.album.views import *

urlpatterns = patterns('api.views',
    url(r'^create/', login_required(CreateV.as_view())),
)
