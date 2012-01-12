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
        context['username'] = self.request.user.username
        return context
    
    def get(self, request, *args, **kwargs):
        user = User.objects.filter(username=request.user.username).get()
        self.queryset = ikr.ImageCopy.objects.filter(owner=user).\
                            order_by('-created')[0:20]
            
        return super(DashboardV, self).get(request, *args, **kwargs)
    
    
class PeopleStreamV(gv.ListView):
    '''List recent images by username'''
    template_name = 'webapp/stream.html'
    
    def get_context_data(self, **kwargs):
        context = super(PeopleStreamV, self).get_context_data(**kwargs)
        context['username'] = self.kwargs['username']
        return context
    
    def get(self, request, username, *args, **kwargs):
        user = User.objects.filter(username=username).get()
        self.queryset = ikr.ImageCopy.objects.filter(owner=user).\
                                              order_by('-created')
            
        return super(PeopleStreamV, self).get(request, *args, **kwargs)

class AlbumV(gv.DetailView):
    '''Show images in an album'''
    model = ikr.Album
    template_name = 'webapp/album.html'  
    
    def get_context_data(self, **kwargs):
        context = super(AlbumV, self).get_context_data(**kwargs)
        context['object_list'] = self.object.imagecopy_set.order_by('-created')
        return context  
    
class SettingsV(gv.TemplateView):
    template_name = 'webapp/settings.html'
