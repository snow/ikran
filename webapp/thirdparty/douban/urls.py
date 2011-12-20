from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.decorators import login_required

from webapp.thirdparty.douban.views import *

urlpatterns = patterns('',
    url(r'^grub_album/', GrubAlbumV.as_view()),    
)