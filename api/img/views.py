# Create your views here.
from django.views.generic import View
from django.http import HttpResponse, HttpResponseRedirect

from core.models import *

class UploadV(View):
    '''
    accept image upload
    
    when complete, either success or not return in one of below:
    * json
    * html page segment
    * redirect
    '''
    def post(self, request, format=None):
        for img in request.FILES.getlist('img'):
            ImageCopy.from_file(img, request.user)
            
        if 'json' == format:
            pass
        elif 'html' == format:
            pass
        elif request.POST['success_uri']:
            # TODO: valid success uri
            return HttpResponseRedirect(request.POST['success_uri'])
        else:
            raise Exception('where did u come from?')