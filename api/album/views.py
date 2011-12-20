# Create your views here.
import json

import django.views.generic as gv
from django.http import HttpResponse, HttpResponseRedirect

import core.models as ikr

class CreateV(gv.View):
    '''
    Create an album
    '''
    def post(self, request):
        album = ikr.Album(title=request.POST['title'], 
                          owner=request.user)
        album.save()
        
        return HttpResponse(json.dumps({'done': True, 
                                        'go_to': '/album/{}/{}/'.\
                                                format(album.id, album.title)}),
                            content_type='application/json')