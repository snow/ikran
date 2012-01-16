#! /usr/bin/env python2.7

#import threading
#from datetime import datetime, timedelta
import time
import argparse
#import signal
#import os
#import urllib2
from os.path import abspath, splitext
from Queue import Queue

#from tweepy import OAuthHandler, API

from pyrcp.django.cli import setup_env
settings = setup_env(__file__)

#from django.core.mail import mail_admins
from django.contrib.auth.models import User
import core.models as ikr
from core.bgservice import BaseBackgroundService
#import lib
import grubbers

class GrubService(BaseBackgroundService):
    _queue_map = None
    _grubber_map = None
    
    def __init__(self):
        super(GrubService, self).__init__()
        
        self._queue_map = {}
        self._grubber_map = {}
        for key in grubbers.list.keys():       
            self._queue_map[key] = Queue()
                        
            grubber = grubbers.list[key](self._queue_map[key])
            grubber.daemon = True
            grubber.start()
            self._grubber_map[key] = grubber
            
    def _shutdown(self):
        super(GrubService, self)._shutdown()
        
        # wait all queued jobs to be done
        for queue in self._queue_map.values():
            queue.join()
    
    def serve(self):
        ''''''
        try:
            job = ikr.GrubJob.objects.order_by('id')[0]
        except IndexError:
            return False
        #print 'got job:', job.source
        
        exist = ikr.ImageCopy.objects.filter(source=job.source, owner=job.user)
        for e in exist:
            # if image with same owner and album exist, skip
            if e.album == job.album:
                job.delete()
                return True
            
        for key in self._queue_map:
            if job.source.split('://')[-1].startswith(key):
                self._queue_map[key].put(job)
                job.delete()
                return True
        
        raise Exception('could not find grubber for ' + job.source)
                
#        grubber = grubbers.get(job.source.split('://')[-1])(job.source)
#        img = ikr.ImageCopy.from_string(grubber.get_data(),
#                                        job.user,
#                                        grubber.get_desc())        
#        img.source = job.source        
#        if job.album:
#            img.album = job.album            
#        img.save()
#            
#        job.delete()        
                                        
#        return True        
            
        
if '__main__' == __name__:
    parser = argparse.ArgumentParser(description='When there are Grub images from remote host')
    parser.add_argument('ACTION', default='start', nargs='?', 
                        choices=('start', 'stop'))
    parser.add_argument('-d', action='store_true', dest='DEBUG', 
                        help='enable debug mode')
    args = parser.parse_args()
    #print parser.parse_args()
    
    pidfile = '{}.pid'.format(splitext(abspath(__file__))[0])
    
    if 'start' == args.ACTION:
        GrubService.start_(pidfile)
        
    elif 'stop' == args.ACTION:        
        GrubService.stop_(pidfile)
    
          