#! /usr/bin/env python2.7

import time
import argparse
from os.path import abspath, splitext
from Queue import Queue

from pyrcp.django.cli import setup_env
settings = setup_env(__file__)

from django.contrib.auth.models import User
import core.models as ikr
from core.bgservice import BaseBackgroundService
import grubbers

class GrubService(BaseBackgroundService):
    '''Load GrubJob from db and distribute to corresponding grubber'''
    _grubber = None
    
    def __init__(self, grubber):
        super(GrubService, self).__init__()        
        self._grubber = grubber
    
    def serve(self):
        ''''''
        try:
            job = ikr.GrubJob.objects.filter(type=self._grubber.TYPE).\
                    order_by('priority', 'id')[0]
        except IndexError:
            return False
        
        if self._grubber.grub(job) is not False:
            job.delete()
            
    @classmethod
    def _init_workers(cls):
        for grubber in grubbers.list:                   
            worker = cls(grubber())
            worker.daemon = True
            worker.start()
            cls._workers.append(worker)
            
        
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
    
          