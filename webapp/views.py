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
    
class ImageListV(gv.TemplateView):
    template_name = 'webapp/imagelist.html'
    
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
    
#class PeopleRecentImagesV(TemplateView):
#    template_name = 'webapp/dashboard.html'    
    
#class InitV(TemplateView):
#    template_name = 'webapp/init.html'
#    
#class ListV(TemplateView):
#    template_name = 'webapp/list.html'
#    
#class TeleportV(TemplateView):
#    template_name = 'webapp/teleport.html'
#    
#class CreateV(TemplateView):
#    '''Render an unbounded create post form'''
#    template_name = 'webapp/post.html'
#    
#    def get(self, request, *args, **kwargs):
#        context = self.get_context_data(**kwargs)
#        context['form'] = CreatePostForm()
#        return self.render_to_response(context)
#    
#class SigninV(TemplateView):  
#    '''Render a signin form which post to api'''
#    template_name = 'webapp/signin.html'
#    
#class SignupV(TemplateView):  
#    '''Render a signup form which post to api'''
#    template_name = 'webapp/signup.html'
#    
#class MeV(RedirectView):
#    permanent = False
#    query_string = True
#
#    def get(self, request, *args, **kwargs):
#        self.url = '/w/user/{}/'.format(request.user.username)
#        return super(MeV, self).get(request, *args, **kwargs)
#
#class UserV(DetailView):
#    model = User
#    slug_field = 'username'
#    template_name = 'webapp/user_profile.html'    