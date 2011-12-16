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
            self.queryset = ikr.ImageCopy.objects.order_by('-created')
            return super(IndexV, self).get(request, *args, **kwargs)


class DashboardV(gv.ListView):
    #template_name = 'webapp/dashboard.html'
    template_name = 'webapp/imagelist.html'
    
    def get_context_data(self, **kwargs):
        context = super(DashboardV, self).get_context_data(**kwargs)
        context['username'] = self.request.user.username
        return context
    
    def get(self, request, *args, **kwargs):
        user = User.objects.filter(username=request.user.username).get()
        self.queryset = ikr.ImageCopy.objects.filter(owner=user).\
                            order_by('-created')
            
        return super(DashboardV, self).get(request, *args, **kwargs) 
    
    
class PeopleStreamV(gv.ListView):
    '''List recent images by username'''
    template_name = 'webapp/imagelist.html'
    
    def get_context_data(self, **kwargs):
        context = super(PeopleStreamV, self).get_context_data(**kwargs)
        context['username'] = self.kwargs['username']
        return context
    
    def get(self, request, username, *args, **kwargs):
        user = User.objects.filter(username=username).get()
        self.queryset = ikr.ImageCopy.objects.filter(owner=user).\
                            order_by('-created').all()
            
        return super(PeopleStreamV, self).get(request, *args, **kwargs)
    
    
class SettingsV(gv.TemplateView):
    template_name = 'webapp/settings.html'
