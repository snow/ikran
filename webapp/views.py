# Create your views here.
import django.views.generic as gv
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User

import core.models as ikr

class UnderConstructionV(gv.TemplateView):
    template_name = 'webapp/under_construction.html'
    
    def get(self, request, *args, **kwargs):
        kwargs['back_to'] = request.META.get('HTTP_REFERER', '/')
        
        return super(UnderConstructionV, self).get(request, *args, **kwargs)


#class IndexV(gv.TemplateView):
#    template_name = 'webapp/index.html'
#    
#    def get(self, request, *args, **kwargs):
#        if request.user.is_authenticated():
#            return HttpResponseRedirect('/dashboard/')
#        else:
#            return super(IndexV, self).get(request, *args, **kwargs)

class IndexV(gv.ListView):
    template_name = 'webapp/index.html'
    
    def get_context_data(self, *args, **kwargs):
        context = super(IndexV, self).get_context_data(*args, **kwargs)
        context['querystring'] = self.request.GET.urlencode()
        return context
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponseRedirect('/dashboard/')
        else:                
            self.queryset = ikr.ImageCopy.objects.order_by('-id')[0:50]
            return super(IndexV, self).get(request, *args, **kwargs)


class DashboardV(gv.ListView):
    #template_name = 'webapp/dashboard.html'
    template_name = 'webapp/stream.html'
    
    def get_context_data(self, **kwargs):
        context = super(DashboardV, self).get_context_data(**kwargs)
        context['owner'] = self.request.user
        return context
    
    def get(self, request, *args, **kwargs):
        user = User.objects.filter(username=request.user.username).get()
        self.queryset = ikr.ImageCopy.objects.filter(owner=user).\
                            order_by('-id')[0:20]
            
        return super(DashboardV, self).get(request, *args, **kwargs)
    
    
class PeopleStreamV(gv.ListView):
    '''List recent images by username'''
    template_name = 'webapp/stream.html'
    
    def get_context_data(self, **kwargs):
        context = super(PeopleStreamV, self).get_context_data(**kwargs)
        context['owner'] = self.kwargs['owner']
        return context
    
    def get(self, request, username, *args, **kwargs):
        user = User.objects.filter(username=username).get()
        self.kwargs['owner'] = user
        self.queryset = ikr.ImageCopy.objects.filter(owner=user).\
                                              order_by('-id')[0:20]
            
        return super(PeopleStreamV, self).get(request, *args, **kwargs)

class AlbumV(gv.DetailView):
    '''Show images in an album'''
    model = ikr.Album
    template_name = 'webapp/album.html'  
    
    def get_context_data(self, **kwargs):
        context = super(AlbumV, self).get_context_data(**kwargs)
        context['object_list'] = self.object.imagecopy_set.order_by('-id')
        context['owner'] = self.object.owner
        return context
    
class PublicStreamV(gv.ListView):
    '''List recent public images'''
    template_name = 'webapp/public_stream.html'
    
    def get(self, request, *args, **kwargs):
        self.queryset = ikr.ImageCopy.objects.order_by('-id')[0:20]
            
        return super(PublicStreamV, self).get(request, *args, **kwargs)
    
class ImageV(gv.DetailView):
    '''Show single image'''
    model = ikr.ImageCopy
    template_name = 'webapp/image.html'  
    slug_field = 'id_str'
    
class SettingsV(gv.TemplateView):
    template_name = 'webapp/settings.html'
