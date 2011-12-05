from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserProfile(models.Model):
    '''
    User profile of ikran
    
    only use for store extra data of an user 
    other models associate with user by django.contrib.auth.models.User
    '''
    user = models.ForeignKey(User, unique=True)
    
#    twitter_id = models.CharField(max_length=255, blank=True)
#    twitter_username = models.CharField(max_length=255, blank=True)
#    twitter_key = models.CharField(max_length=255, blank=True)
#    twitter_secret = models.CharField(max_length=255, blank=True)
#    
#    flikcr_id = models.CharField(max_length=255, blank=True)
#    flikcr_username = models.CharField(max_length=255, blank=True)
#    flikcr_key = models.CharField(max_length=255, blank=True)
#    flikcr_secret = models.CharField(max_length=255, blank=True)
    
class ImageFile(models.Model):
    '''
    A persistenced image file under lying of a ImageCopy
    
    Could have multiple references, each owned by unique user.
    Also may have no reference. Maybe gabage collected at this situation.
    '''    
    filepath = models.CharField(max_length=255, unique=True)
    md5 = models.CharField(max_length=255, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    
    # in pixels
    width_f = models.PositiveSmallIntegerField()
    height_f = models.PositiveSmallIntegerField()
    width_l = models.PositiveSmallIntegerField()
    height_l = models.PositiveSmallIntegerField()
    width_m = models.PositiveSmallIntegerField()
    height_m = models.PositiveSmallIntegerField()
    width_s = models.PositiveSmallIntegerField()
    height_s = models.PositiveSmallIntegerField()
    width_tl = models.PositiveSmallIntegerField()
    height_tl = models.PositiveSmallIntegerField()
    width_tm = models.PositiveSmallIntegerField()
    height_tm = models.PositiveSmallIntegerField()
    width_ts = models.PositiveSmallIntegerField()
    height_ts = models.PositiveSmallIntegerField() 

class Album(models.Model):
    '''
    Album
    '''
    title = models.CharField(max_length=255, unique=True)
    owner = models.ForeignKey(User)
    created = models.DateTimeField(auto_now_add=True)
    
class Tag(models.Model):
    '''
    Tag
    '''
    text = models.CharField(max_length=255, unique=True)
    created = models.DateTimeField(auto_now_add=True)
        
class ImageCopy(models.Model):
    '''
    A reference to ImageFile.
    
    Owned by unique user
    '''
    id_str = models.CharField(max_length=255, unique=True)
    description = models.CharField(max_length=255, unique=True)
    # serilzed exif data
    exif_str = models.TextField(blank=True)
    
    owner = models.ForeignKey(User)
    album = models.ForeignKey(Album, null=True, blank=True)
    tags = models.ManyToManyField(Tag, related_name='images')
    created = models.DateTimeField(auto_now_add=True)
    
    file = models.ForeignKey(ImageFile)
    
    T_LOCAL = 0
    T_TWITTER = 1
    T_FLICKER = 2
    SOURCE_TYPES = {
        T_LOCAL: 'local',
        T_FLICKER: 'flickr',        
        T_TWITTER: 'twitter',
    }
    source = models.PositiveSmallIntegerField(choices=SOURCE_TYPES.items(), 
                                              default=T_LOCAL)
    external_id = models.CharField(max_length=255, blank=True)
    external_data = models.TextField(blank=True)
    
    
