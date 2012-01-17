from lib import save_image, BaseHTMLParser   

from pyrcp.django.cli import setup_env
settings = setup_env(__file__)

import core.models as ikr

class DoubanPhotoHTMLParser(BaseHTMLParser):
    '''Parse photo view page in douban'''
    _in_mainphoto_wrapper = False
    _in_photo_desc = False
    _depth_in_photo_desc = 0    
    
    def handle_starttag(self, tag, attrs):
        if 'a' == tag:
            d = {key: value for(key, value) in attrs}
            if 'class' in d and 'mainphoto' == d['class']:
                self._in_mainphoto_wrapper = True
                
        elif 'div' == tag:
            if self._in_photo_desc:
                self._depth_in_photo_desc += 1
            else:
                d = {key: value for(key, value) in attrs}
                if 'class' in d and 'photo_descri' == d['class']:
                    self._in_photo_desc = True
            
        elif self._in_mainphoto_wrapper and 'img' == tag:
            d = {key: value for(key, value) in attrs}
            self._uri = d['src']
                
    def handle_data(self, data):
        if self._in_photo_desc:
            self._desc = data
            
    def handle_endtag(self, tag):
        if self._in_mainphoto_wrapper and 'a' == tag:
            self._in_mainphoto_wrapper = False
                
        if self._in_photo_desc and 'div' == tag:
            if 0 == self._depth_in_photo_desc:
                self._depth_in_photo_desc -= 1
            else:
                self._in_photo_desc = False


class PhotoGrubber(object):
    ''''''
    TYPE = 'douban.photo'
    
    def grub(self, job):
        uri = job.data
        
        src, desc = DoubanPhotoHTMLParser.parse_uri(uri)
        if src:
            save_image(src, job.user, referer=uri, desc=desc, album=job.album)            
        else:
            raise Exception('failed to parse {}, is it a douban photo?'.\
                            format(source))
