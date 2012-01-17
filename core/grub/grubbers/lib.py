import urllib2
import threading
from HTMLParser import HTMLParser

from pyrcp.django.cli import setup_env
settings = setup_env(__file__)

from django.core.mail import mail_admins

import core.models as ikr

_DEFAULT_UA = 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 ' + \
                '(KHTML, like Gecko) Chrome/16.0.912.63 Safari/535.7'

class UnsupportedTypeError(Exception):
    def __init__(self, type):
        super(UnsupportedTypeError, self).__init__()
        self.message = 'response type {} is not supported'.format(type)                
                
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


def save_image(src, owner, referer='', desc='', album=False):
    if '://' not in src:
        src = 'http://' + src
        
    if '://' not in referer:
        referer = 'http://' + referer
        
    exist = ikr.ImageCopy.objects.filter(source=referer, owner=owner)
    for e in exist:
        # if image with same owner and album exist, skip
        if e.album == album:
            return
    
    request = urllib2.Request(src, headers={
                                       'User-Agent': _DEFAULT_UA,
                                       'Referer': referer
                                   })
    conn = urllib2.urlopen(request)
    
    if 'image' != conn.headers.getmaintype():
        raise UnsupportedTypeError(conn.headers.gettype())
    
    raw_data = conn.read()
    
    img = ikr.ImageCopy.from_string(raw_data, owner, desc)
    img.source = referer
    if album:
        img.album = album            
    img.save()


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

