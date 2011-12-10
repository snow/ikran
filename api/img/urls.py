from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.decorators import login_required

from api.img.views import *

urlpatterns = patterns('api.views',
    url(r'^upload/', login_required(UploadV.as_view())),                   
    url(r'^upload.(?P<format>json|html)', login_required(UploadV.as_view())),
    #url(r'^gruburi.(?P<format>json|html)', ''),
)
