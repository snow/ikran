# Create your views here.
import tempfile
import json

from django.views.generic import View
from django.http import HttpResponse, HttpResponseRedirect
from django.core.files import File

import core.models as ikr

class UploadRawV(View):
    '''
    accept image uploaded as raw post data
    
    response in json
    '''
    def post(self, request):
        tmp = tempfile.NamedTemporaryFile()
        tmp.write(request.raw_post_data)
        tmp.flush()
        img = ikr.ImageCopy.from_file(File(tmp), request.user, 
                                      request.GET.get('filename', ''))
        tmp.close()
        
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
         
        for img in request.FILES.getlist('img'):
            img = ikr.ImageCopy.from_file(img, request.user, img.name)
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