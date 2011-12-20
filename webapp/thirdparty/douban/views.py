# Create your views here.
import json

from django.http import HttpResponse, HttpResponseRedirect
import django.views.generic as gv

import grub_album
import core.models as ikr

class GrubAlbumV(gv.View):
    '''TODO'''
    def post(self, request, *args, **kwargs):        
        ag = grub_album.AlbumGrubber(request.POST['uri'],
                                     request.user,
                                     ua=request.META.get('HTTP_USER_AGENT')) 
                                     #referer=request.META.get('HTTP_REFERER'))            
        album = ag.get_album()
        
        return HttpResponse(json.dumps({
                                'done': True,
                                'go_to': u'/album/{}/{}/'.format(album.id, 
                                                                album.title)
                            }),
                            content_type='application/json')
         