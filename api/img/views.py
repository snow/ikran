# Create your views here.
import tempfile
import json

from django.views.generic import View, ListView
from django.http import HttpResponse, HttpResponseRedirect
from django.core.files import File
from django.contrib.auth.models import User

import core.models as ikr

class PublicListV(ListView):
    template_name = 'webapp/com/plain_imgls.html'
    
    def get(self, request, since=0, till=0, count=20, format='html',
            *args, **kwargs):
        ''''''
        qs = ikr.ImageCopy.objects.order_by('-id')
        
        if since:
            qs = qs.filter(pk__gt=since)
            
        if till:
            qs = qs.filter(pk__lt=till)
        
        if not count:
            count = 20
            
        qs = qs[0:count]
        
        if 'json' == format:
            results = []
            for el in qs:
                results.append(el.get_dict())
                
            return HttpResponse(json.dumps(dict(done=True, 
                                                results=results)),
                                content_type='application/json')
            
        else:     
            self.queryset = qs       
            return super(PublicListV, self).get(request, *args, **kwargs)
    
class MineListV(ListView):
    template_name = 'webapp/com/plain_imgls.html'
    
    def get(self, request, since=0, till=0, count=20, format='html',
            *args, **kwargs):
        ''''''
        qs = ikr.ImageCopy.objects.filter(owner=request.user).order_by('-id')
        
        if since:
            qs = qs.filter(pk__gt=since)
            
        if till:
            qs = qs.filter(pk__lt=till)
        
        if not count:
            count = 20
            
        qs = qs[0:count]
        
        if 'json' == format:
            results = []
            for el in qs:
                results.append(el.get_dict())
                
            return HttpResponse(json.dumps(dict(done=True, 
                                                results=results)),
                                content_type='application/json')
            
        else:     
            self.queryset = qs       
            return super(MineListV, self).get(request, *args, **kwargs)

class PeopleListV(ListView):
    template_name = 'webapp/com/plain_imgls.html'
    
    def get(self, request, username, since=0, till=0, count=20, format='html',
            *args, **kwargs):
        ''''''
        user = User.objects.get(username=username)
        qs = ikr.ImageCopy.objects.filter(owner=user).order_by('-id')
        
        if since:
            qs = qs.filter(pk__gt=since)
            
        if till:
            qs = qs.filter(pk__lt=till)
        
        if not count:
            count = 20
        
        qs = qs[0:count]
        
        import logging
        l = logging.getLogger('c')
        l.debug(count)
        
        if 'json' == format:
            results = []
            for el in qs:
                results.append(el.get_dict())
                
            return HttpResponse(json.dumps(dict(done=True, 
                                                results=results)),
                                content_type='application/json')
            
        else:     
            self.queryset = qs       
            return super(PeopleListV, self).get(request, *args, **kwargs)

class UploadRawV(View):
    '''
    accept image uploaded as raw post data
    
    response in json
    '''
    def post(self, request):
        album_id = int(request.GET.get('album_id', 0))
        if album_id:
            album = ikr.Album.objects.filter(id=album_id).get()
        else:
            album = False
        
        tmp = tempfile.NamedTemporaryFile()
        tmp.write(request.raw_post_data)
        tmp.flush()
        img = ikr.ImageCopy.from_file(File(tmp), request.user, 
                                      request.GET.get('filename', ''))
        tmp.close()
        
        if album:
            img.album = album
            img.save()
        
        return HttpResponse(json.dumps(dict(done=True, 
                                            result=img.get_dict())),
                            content_type='application/json')

class UploadFormV(View):
    '''
    accept image uploaded in form
    
    when complete, either success or not return in one of below:
    * json
    * html page segment
    * redirect
    '''
    
    def post(self, request, format=None):
        results = []
        
        album_id = int(request.POST.get('album_id', 0))
        if album_id:
            album = ikr.Album.objects.filter(id=album_id).get()
         
        for img in request.FILES.getlist('img'):
            img = ikr.ImageCopy.from_file(img, request.user, img.name)
            
            if album:
                img.album = album
                img.save()
            
            results.append(img.get_dict())
            
        if 'json' == format:
            return HttpResponse(json.dumps(dict(done=True, results=results)),
                    content_type='application/json')
        elif 'html' == format:
            raise NotImplemented()
        elif request.POST['success_uri']:
            # TODO: valid success uri
            return HttpResponseRedirect(request.POST['success_uri'])
        else:
            raise Exception('where did u come from?')
        
class BatchDeleteV(View):
    '''accept comma separated ImageCopy ids and delete them'''
    
    def post(self, request, format='json'):
        imgs = []
        
        for id in request.POST['ids'].split(','):
            img = ikr.ImageCopy.objects.get(pk=id)
            
            # TODO: use perm instead
            if img.owner != request.user:
                raise Exception('u dont have perm to del this pic')
            else:
                imgs.append(img)
                
        for img in imgs:
            img.delete()
                
        if 'json' == format:
            return HttpResponse(json.dumps(dict(done=True)),
                                content_type='application/json')
            
        elif 'html' == format:
            raise NotImplemented()
        
        elif request.POST['success_uri']:
            # TODO: valid success uri
            return HttpResponseRedirect(request.POST['success_uri'])
        else:
            raise Exception('where did u come from?')
            
            
        