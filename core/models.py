import json
import hashlib
import os
import logging
from datetime import datetime
import tempfile

from django.db import models
from django.db.models.fields.files import FieldFile
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.core.files import File
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.dispatch import receiver
from PIL import Image
import pyexiv2 
from pyrcp import struk

# Create your models here.
class UserProfile(models.Model):
    '''
    User profile of ikran
    
    only use for store extra data of an user 
    other models associate with user by django.contrib.auth.models.User
    '''
    user = models.ForeignKey(User, unique=True)
    
@receiver(post_save, sender=User, 
          dispatch_uid='ikran.core.models.createuserprofile')
def _user_create_receiver(instance, created, **kwargs):
    '''Create empty user profile on user model created'''
    if created:
        profile = UserProfile(user=instance)
        profile.save()    
    
class ImageFile(models.Model):
    '''
    A persistenced image file under lying of a ImageCopy
    
    Could have multiple references, each owned by unique user.
    Also may have no reference. Maybe gabage collected at this situation.
    '''
    SIZE_FULL = 'f'
    SIZE_LARGE = 'l'
    SIZE_MEDIAN = 'm'
    SIZE_SMALL = 's'
    SIZE_THUMB_LARGE = 'tl'
    SIZE_THUMB_MEDIAN = 'tm'
    SIZE_THUMB_SMALL = 'ts'
    
    SIZE_LIMITS = {
        SIZE_LARGE: (1024, 800),
        SIZE_MEDIAN: (640, 640),
        SIZE_SMALL: (180, 180),
        SIZE_THUMB_LARGE: (180, 180),
        SIZE_THUMB_MEDIAN: (120, 120),
        SIZE_THUMB_SMALL: (72, 72),
    }
    
    @classmethod
    def md5sum(cls, file):
        '''
        Calculate md5 sum of given file
        '''
        # md5
        md5 = hashlib.md5()
        
        if file.multiple_chunks():
            for chunk in file.chunks():
                md5.update(chunk)
        else:
            file.seek(0)
            md5.update(file.read())
            
        return md5.hexdigest()
    
    def gen_dirname(self):
        return datetime.now().strftime('uimg/%Y/%m/%d')
    
    def gen_filename(self, size=SIZE_FULL):
        if self.SIZE_FULL == size:
            size = ''
        else:
            size = '_' + size
        
        return '{dir}/{id_str}{size}.jpg'.format(dir=self.gen_dirname(), 
                                                 id_str=self.id_str, size=size)
        
    def resample(self):
        '''Generate image file of all sizes from FULL'''
        img_f = Image.open(self.file.path)
        imgpath_noext = os.path.splitext(self.file.path)[0]
        ORIGIN_WIDTH = img_f.size[0]
        ORIGIN_HEIGHT = img_f.size[1]
        
        for size in self.SIZE_LIMITS:
            # resize and crop for thumb sizes
            if 't' == size[0]:
                # resize based on the shorter edge
                if ORIGIN_WIDTH > ORIGIN_HEIGHT:
                    new_height = self.SIZE_LIMITS[size][1]
                    scale = float(new_height) / ORIGIN_HEIGHT
                    new_width = int(ORIGIN_WIDTH * scale)
                    
                    left = new_width / 2 - self.SIZE_LIMITS[size][0] / 2
                    upper = 0
                    right = new_width / 2 + self.SIZE_LIMITS[size][0] / 2
                    lower = new_height
                else:
                    new_width = self.SIZE_LIMITS[size][0]
                    scale = float(new_width) / ORIGIN_WIDTH
                    new_height = int(ORIGIN_HEIGHT * scale)
                    
                    left = 0
                    upper = 0
                    right = self.SIZE_LIMITS[size][0]
                    lower = self.SIZE_LIMITS[size][1]                    
                    
                curimg = img_f.resize((new_width, new_height), 
                                      Image.ANTIALIAS).\
                               crop((left, upper, right, lower))
            # resize for normal sizes
            else:            
                scale = False
                if ORIGIN_WIDTH > self.SIZE_LIMITS[size][0]:
                    new_width = self.SIZE_LIMITS[size][0]
                    scale = float(new_width) / ORIGIN_WIDTH
                else:
                    new_width = ORIGIN_WIDTH
                
                if scale:
                    new_height = int(ORIGIN_HEIGHT * scale)
                else:
                    new_height = ORIGIN_HEIGHT
                    
                if new_height > self.SIZE_LIMITS[size][1]:
                    new_height = self.SIZE_LIMITS[size][1]
                    scale = float(new_height) / ORIGIN_HEIGHT
                    new_width = int(ORIGIN_WIDTH * scale)
                
                curimg = img_f.resize((new_width, new_height), Image.ANTIALIAS)
                
            curpath = '{}_{}.jpg'.format(imgpath_noext, size)    
            curimg.save(curpath)
    
    @classmethod
    def from_file(cls, file):
        '''
        Construct an ImageFile from file
        '''
        md5 = cls.md5sum(file)
        
        try:
            imgf = cls.objects.filter(md5=md5).get()
        except ImageFile.DoesNotExist:
            imgf = cls(md5=md5)
            imgf.save()
            
            try:
                imgf.id_str = struk.int2str(imgf.id)
                imgf.file = FieldFile(imgf, imgf.file, imgf.gen_filename())
                imgf.save()
                
                dir = os.path.dirname(imgf.file.path)
                if not os.path.exists(dir):    
                    os.makedirs(dir)
                
                # make sure converted to jpg
                if isinstance(file, InMemoryUploadedFile):
                    tmp = tempfile.NamedTemporaryFile()
                    file.seek(0)
                    tmp.write(file.read())
                    tmp.flush()
                    img = Image.open(tmp.name)
                else:
                    img = Image.open(file.temporary_file_path())
                
                img.save(imgf.file.path)
                del img
                imgf.resample()
            except:
                imgf.delete()
                raise
        
        return imgf
        
    id_str = models.CharField(max_length=255, unique=True)
    md5 = models.CharField(max_length=255, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    
    file = models.ImageField(upload_to=gen_filename, null=True)

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
    description = models.CharField(max_length=255)
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
    
    @classmethod
    def from_filename(cls, filename, user):
        '''
        Construct an ImageCopy from an filepath
        '''
        return cls.from_filen(File(open(filename)), user)
    
    @classmethod
    def from_file(cls, file, user):
        '''
        Construct an ImageCopy from an uploaded file
        '''
        img = ImageCopy(owner=user)
        
        # strip exif from given image
        file.seek(0)
        exif = pyexiv2.ImageMetadata.from_buffer(file.read())
        exif.read()
        
        exif_dict = dict()
        for k in exif.exif_keys:
            try:
                exif_dict[exif[k].label] = exif[k].human_value.decode('utf-8')
            except UnicodeDecodeError:
                # ignore invalid chars
                pass
            
            del exif[k]
            
        img.exif_str = json.dumps(exif_dict)
            
        img.file = ImageFile.from_file(file)
        img.save()
        
        return img