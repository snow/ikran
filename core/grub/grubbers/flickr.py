import flickrapi

from lib import save_image

from pyrcp.django.cli import setup_env
settings = setup_env(__file__)

#from django.core.mail import mail_admins

import core.models as ikr
from pyfyd.models import FlickrAccount

def _get_client(account):
    return flickrapi.FlickrAPI(settings.FLICKR_CONSUMER_KEY,
                               settings.FLICKR_CONSUMER_SECRET,
                               token=account.token,
                               store_token=False)

class PeopleStreamGrubber(object):
    ''''''
    TYPE = 'flickr.people'
    
    def grub(self, job):
        account = FlickrAccount.objects.get(owner=job.user)
        client = _get_client(account)
        
        resp = client.photosets_getList()
        for photoset in resp.getiterator('photoset'):
            set_id = photoset.attrib['id']
            set_uri = 'http://www.flickr.com/photos/{user}/sets/{id}/'.\
                        format(user=account.username, id=set_id)
            
            try:
                album = ikr.Album.objects.get(source=set_uri, owner=job.user)
            except ikr.Album.DoesNotExist:
                album = ikr.Album(owner=job.user, source=set_uri, 
                                  title=photoset.find('title').text)
                album.save()
            
            album_job = ikr.GrubJob(type=PhotosetGrubber.TYPE, 
                                    data=set_id, album=album, user=job.user, 
                                    priority=ikr.GrubJob.MID_PRIORITY)
            album_job.save()
            
        resp = client.photos_getNotInSet()
        for photo in resp.getiterator('photo'):
            photo_job = ikr.GrubJob(type=PhotoGrubber.TYPE, 
                                    data=photo.attrib['id'], album=album, 
                                    user=job.user)
            photo_job.save()
    
class PhotosetGrubber(object):
    ''''''
    TYPE = 'flickr.set'
    
    def grub(self, job):
        account = FlickrAccount.objects.get(owner=job.user)
        client = _get_client(account)
        
        set_id = job.data
        resp = client.photosets_getPhotos(photoset_id=set_id)
            
        for photo in resp.getiterator('photo'):
            photo_job = ikr.GrubJob(type=PhotoGrubber.TYPE, 
                                    data=photo.attrib['id'], album=job.album, 
                                    user=job.user)
            photo_job.save()
            
    
class PhotoGrubber(object):
    ''''''
    TYPE = 'flickr.photo'
    
    def grub(self, job):
        account = FlickrAccount.objects.get(owner=job.user)
        client = _get_client(account)
        
        photo_id = job.data
        
        resp = client.photos_getSizes(photo_id=photo_id)
            
        area = 0
        source = None
        uri = None
        for size in resp.getiterator('size'):
            cur_area = int(size.attrib['width']) * \
                       int(size.attrib['height'])
            if cur_area >= area:
                area = cur_area
                source = size.attrib['source']
                uri = size.attrib['url']
        
        resp = client.photos_getInfo(photo_id=photo_id)
        
        title = None
        desc = None
                
        for tag in resp.find('photo'):
            tagname = tag.tag
            if 'video' == tagname:
                return
            elif 'title' == tagname:
                title = tag.text
            elif 'description' == tagname:
                desc = tag.text
        
        desc = (title or '') + '\n' + (desc or '')
                
        save_image(source, job.user, referer=uri, desc=desc, album=job.album)
