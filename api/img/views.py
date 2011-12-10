# Create your views here.
import tempfile
import json

from django.views.generic import View
from django.http import HttpResponse, HttpResponseRedirect
from django.core.files import File

import core.models as ikr

class UploadV(View):
    '''
    accept image upload
    
    when complete, either success or not return in one of below:
    * json
    * html page segment
    * redirect
    '''
    def post(self, request, format=None):
        import logging
        l = logging.getLogger('c')
        
        imgls = []
    
        if 'filename' in request.GET:
            tmp = tempfile.NamedTemporaryFile()
            tmp.write(request.raw_post_data)
            tmp.flush()
            img = ikr.ImageCopy.from_file(File(tmp), request.user)
            tmp.close()
            imgls.append(dict(id=img.id, urs_s=img.uri_s()))
        else:        
            for img in request.FILES.getlist('img'):
                img = ikr.ImageCopy.from_file(img, request.user)
                imgls.append(dict(id=img.id, urs_s=img.uri_s()))
                
        if 'json' == format:
            return HttpResponse(json.dumps({
                            'done': True,
                            'success': True,
                            'results': json.dumps(imgls) 
                        }),
                        content_type='application/json')
        elif 'html' == format:
            raise NotImplemented()
        elif request.POST['success_uri']:
            # TODO: valid success uri
            return HttpResponseRedirect(request.POST['success_uri'])
        else:
            raise Exception('where did u come from?')