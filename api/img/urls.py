from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.decorators import login_required

from api.img.views import *

urlpatterns = patterns('api.views',    
    url(r'^list/public/?(?P<count>\d+)?\.?(?P<format>\w*)/$', 
        PublicListV.as_view()),
    url(r'^list/public/since(?P<since>\d+)/?(?P<count>\d+)?\.?(?P<format>\w*)/$', 
        PublicListV.as_view()),
    url(r'^list/public/since(?P<since>\d+)/till(?P<till>\d+)/?(?P<count>\d+)?\.?(?P<format>\w*)/$', 
        PublicListV.as_view()),
    url(r'^list/public/till(?P<till>\d+)/?(?P<count>\d+)?\.?(?P<format>\w*)/$', 
        PublicListV.as_view()),
    url(r'^list/public/till(?P<till>\d+)/since(?P<since>\d+)/?(?P<count>\d+)?\.?(?P<format>\w*)/$', 
        PublicListV.as_view()),
                       
    url(r'^list/people/(?P<username>.+)/(?P<count>\d+)?/?\.?(?P<format>\w*)/$', 
        PeopleListV.as_view()),
    url(r'^list/people/(?P<username>.+)/since(?P<since>\d+)/(?P<count>\d+)?/?\.?(?P<format>\w*)/$', 
        PeopleListV.as_view()),
    url(r'^list/people/(?P<username>.+)/since(?P<since>\d+)/till(?P<till>\d+)/(?P<count>\d+)?/?\.?(?P<format>\w*)/$', 
        PeopleListV.as_view()),
    url(r'^list/people/(?P<username>.+)/till(?P<till>\d+)/?(?P<count>\d+)?/?\.?(?P<format>\w*)/$', 
        PeopleListV.as_view()),
    url(r'^list/people/(?P<username>.+)/till(?P<till>\d+)/since(?P<since>\d+)/(?P<count>\d+)?/?\.?(?P<format>\w*)/$', 
        PeopleListV.as_view()),                                          
                       
    url(r'^upload/', login_required(UploadFormV.as_view())),                   
    url(r'^upload.(?P<format>json|html)$', login_required(UploadFormV.as_view())),
    
    url(r'^uploadraw/$', login_required(UploadRawV.as_view())),
    #url(r'^gruburi.(?P<format>json|html)', ''),
    
    url(r'^delete/$', login_required(BatchDeleteV.as_view())),
)
