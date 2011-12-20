#! /usr/bin/env python
import sys
import time
import urllib2
import argparse
import subprocess
from HTMLParser import HTMLParser
from os.path import abspath
import logging

from pyrcp.django.cli import setup_env

settings = setup_env(__file__)

from django.contrib.auth.models import User
import core.models as ikr

_DEFAULT_REF = 'http://shuo.douban.com/'
_DEFAULT_UA = 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 ' + \
                '(KHTML, like Gecko) Chrome/16.0.912.63 Safari/535.7'
_BREATH_TIMEOUT = 1
                
class Request(urllib2.Request):
    '''TODO'''
    ua = _DEFAULT_UA
    referer = _DEFAULT_REF
    
    @classmethod
    def get_content(cls, uri):
        '''
        shortcut method to build a request with ua and ref, 
        then read content from response
        '''
        if not uri.startswith('http://'):
            uri = 'http://' + uri
            
        request = cls(uri, headers={'User-Agent': cls.ua, 
                                    'Referer': cls.referer})        
    
        conn = urllib2.urlopen(request)
        encoding = conn.headers.getparam('charset')
        return conn.read().decode(encoding)

class AlbumHTMLParser(HTMLParser):
    '''Parse photo list page of a douban album'''    
    _title = None
    _imgls = None
    
    _in_title = False
    
    def handle_starttag(self, tag, attrs):  
        if 'h1' == tag:
            self._in_title = True
        
        elif 'a' == tag:
            d = {key: value for(key, value) in attrs}
            if 'class' in d and 'photolst_photo' == d['class']:
                self._imgls.append(d['href'])    
            
        elif 'link' == tag :
            d = {key: value for(key, value) in attrs}            
            if 'rel' in d and 'next' == d['rel']:
                time.sleep(_BREATH_TIMEOUT)
                self.parse_uri(d['href'], imgls=self._imgls)
        
                
    def handle_data(self, data):
        if self._in_title:
            self._title = data.split('-', 1)[1].strip()                        
                
    def handle_endtag(self, tag):
        if self._in_title:
            self._in_title = False
    
    @classmethod            
    def parse_uri(cls, uri, imgls=None):
        parser = cls()
        parser._imgls = imgls or []
        parser.feed(Request.get_content(uri))
        return parser._title, parser._imgls
        
        
class PhotoHTMLParser(HTMLParser):
    '''Parse photo view page in douban'''
    _in_mainphoto_wrapper = False
    _in_photo_desc = False
    _depth_in_photo_desc = 0
    
    _uri = None 
    _desc = ''    
    
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
    
    @classmethod            
    def parse_uri(cls, uri):
        parser = cls()
        parser.feed(Request.get_content(uri))
        return parser._uri, parser._desc        

class AlbumGrubber(object):
    '''TODO'''
    _title = None
    _imgls = None
    _album = None
    
    def __init__(self, uri, user, ua=None, referer=None):
        if '://' not in uri:
            uri = 'http://' + uri
        
        # build command for later call
        cmd = [sys.executable, abspath(__file__)]    
        
        if ua:
            Request.ua = ua     
            cmd.append('--ua='+ua)   
        if referer:
            Request.referer = referer
            # no need to pass referer
            #cmd.append('--ref='+referer)
            
        self._title, self._imgls = AlbumHTMLParser.parse_uri(uri)
        self._album = ikr.Album(title=self._title, owner=user)
        self._album.save()
        
        cmd.append('--album_id='+str(self._album.id))
        cmd.extend(self._imgls)
        
        # call this module as background script
        #l = logging.getLogger('d')
        #    l.debug(cmd)
        subprocess.Popen(cmd)
        
    def get_album(self):
        return self._album    


#
# let's jean!
# -------------
#
if '__main__' == __name__:
    parser = argparse.ArgumentParser(
                          description='grub images from douban')
    parser.add_argument('IMG_LS', nargs='+')
#    parser.add_argument('-u', '--uid', dest='UID', nargs='?')
    parser.add_argument('-a', '--album_id', dest='ALBUM_ID')
#    parser.add_argument('-r', '--ref', dest='REF', nargs='?')
    parser.add_argument('-ua', '--ua', dest='UA', nargs='?')
    parser.add_argument('-d', action='store_true', dest='DEBUG', 
                        help='enable debug mode')
    parser.add_argument('-t', action='store_true', dest='TEST', 
                        help='enable test mode')
    args = parser.parse_args()
    
    try:
        album = ikr.Album.objects.filter(id=args.ALBUM_ID).get()    
        user = album.owner
        
        if args.UA:
            Request.ua = args.UA
        
        for uri in args.IMG_LS:            
            src, desc = PhotoHTMLParser.parse_uri(uri)
            
            request = urllib2.Request(src)
            request.add_header('Referer', uri)
            if args.UA:
                request.add_header('User-Agent', args.UA)
                
            resp = urllib2.urlopen(request).read()
            #l.debug(resp)
            img = ikr.ImageCopy.from_string(resp, user, desc)
            img.album = album
            img.save()
            
            time.sleep(2*_BREATH_TIMEOUT)
            
    except Exception as err:
        l = logging.getLogger('d')
        l.debug(err.message)
        raise