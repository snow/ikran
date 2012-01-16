import urllib2
import threading
from HTMLParser import HTMLParser

from pyrcp.django.cli import setup_env
settings = setup_env(__file__)

from django.core.mail import mail_admins

import core.models as ikr

_DEFAULT_UA = 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 ' + \
                '(KHTML, like Gecko) Chrome/16.0.912.63 Safari/535.7'
                
                
def get_html(uri):
    if '://' not in uri:
        uri = 'http://' + uri
    
    request = urllib2.Request(uri, headers={'User-Agent': _DEFAULT_UA})              
    conn = urllib2.urlopen(request)
    
    if 'text/html' != conn.headers.gettype():
        raise Exception('response is not html: '+conn.headers.gettype())
    
    resp = conn.read()
    
    encoding = conn.headers.getparam('charset')        
    if encoding:        
        resp = resp.decode(encoding)
        
    return resp

def get_image(uri, referer):
    if '://' not in uri:
        uri = 'http://' + uri
    
    request = urllib2.Request(uri, headers={
                                       'User-Agent': _DEFAULT_UA,
                                       'Referer': referer
                                   })               
    conn = urllib2.urlopen(request)
    
    if 'image' != conn.headers.getmaintype():
        raise Exception('response is not html: '+conn.headers.gettype())
    
    return conn.read()


class BaseHTMLParser(HTMLParser):
    ''''''
    _uri = None 
    _desc = ''
    
    @classmethod            
    def parse_uri(cls, uri):
        return cls.parse_content(get_html(uri))
    
    @classmethod
    def parse_content(cls, content):
        parser = cls()
        parser.feed(content)
        return parser._uri, parser._desc


#class BaseGrubber(object):
#    '''Interface of image grubber'''
#    def __init__(self, source):
#        ''''''
#        raise NotImplementedError()
#        
#    def get_data(self):
#        ''''''
#        raise NotImplementedError()
#    
#    def get_desc(self):
#        ''''''
#        raise NotImplementedError()

class BaseGrubber(threading.Thread):
    '''Base class of image grubber'''
    __queue = None
    
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.__queue = queue
    
    def run(self):
        while True:
            job = self.__queue.get()
            
            raw_data, desc = self.grub(job)
                        
            img = ikr.ImageCopy.from_string(raw_data, job.user, desc)        
            img.source = job.source        
            if job.album:
                img.album = job.album            
            img.save()
            
            self.__queue.task_done()
    
    def grub(self, job):
        '''Should return raw image data string and description string in tuple'''
        raise NotImplementedError()
    
    @classmethod
    def _on_exception(cls, err):
        mail_admins('exception in {}'.format(cls.__name__), err)