from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.decorators import login_required

from api.img.views import *

urlpatterns = patterns('api.views',    
    url(r'^list/public\.?(?P<format>\w*)/(?P<count>\d+)?/?$', 
        PublicListV.as_view()),
    url(r'^list/public\.?(?P<format>\w*)/since(?P<since>\d+)/(?P<count>\d+)?/?$', 
        PublicListV.as_view()),
    url(r'^list/public\.?(?P<format>\w*)/since(?P<since>\d+)/till(?P<till>\d+)/(?P<count>\d+)?/?$', 
        PublicListV.as_view()),
    url(r'^list/public\.?(?P<format>\w*)/till(?P<till>\d+)/(?P<count>\d+)?/?$', 
        PublicListV.as_view()),
    url(r'^list/public\.?(?P<format>\w*)/till(?P<till>\d+)/since(?P<since>\d+)/(?P<count>\d+)?/?$', 
        PublicListV.as_view()),
                       
    url(r'^list/mine\.?(?P<format>\w*)/(?P<count>\d+)?/?$', 
        MineListV.as_view()),
    url(r'^list/mine\.?(?P<format>\w*)/since(?P<since>\d+)/(?P<count>\d+)?/?$', 
        MineListV.as_view()),
    url(r'^list/mine\.?(?P<format>\w*)/since(?P<since>\d+)/till(?P<till>\d+)/(?P<count>\d+)?/?$', 
        MineListV.as_view()),
    url(r'^list/mine\.?(?P<format>\w*)/till(?P<till>\d+)/(?P<count>\d+)?/?$', 
        MineListV.as_view()),
    url(r'^list/mine\.?(?P<format>\w*)/till(?P<till>\d+)/since(?P<since>\d+)/(?P<count>\d+)?/?$', 
        MineListV.as_view()),                                          
                       
    url(r'^upload/', login_required(UploadFormV.as_view())),                   
    url(r'^upload.(?P<format>json|html)$', login_required(UploadFormV.as_view())),
    
    url(r'^uploadraw/$', login_required(UploadRawV.as_view())),
    #url(r'^gruburi.(?P<format>json|html)', ''),
    
    url(r'^delete/$', login_required(BatchDeleteV.as_view())),
)
