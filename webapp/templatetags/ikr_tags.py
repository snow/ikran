from django import template
from django.template import Library, Context, Template
from django.conf import settings
#from django.contrib.auth.models import User

import core.models as ikr

register = template.Library()

@register.simple_tag
def album_list(user, current=None):
    #album_list = ikr.Album.objects.filter(owner=user)
    
    tpl = template.loader.get_template('webapp/com/albumls.html')
    
    return tpl.render(template.Context({
               'object_list': ikr.Album.objects.filter(owner=user.id), # access id to force simple lazy object to load
               'current': current
           }))