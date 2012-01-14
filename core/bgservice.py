import threading
import time
import signal
import os
import sys
import traceback

def _interrupt_handler(signum, frame):
    if signal.SIGINT == signum:
        raise KeyboardInterrupt
    
def _get_pid(pidfile):
    try:
        pid_file = open(pidfile, 'r')
    except IOError as err:
        if 2 == err.errno:
            return None # pidfile not exist
        else:
            raise # dont know what happend, let propagete
    else:
        pid = int(pid_file.read())
        pid_file.close()
        return pid    

class BaseBackgroundService(threading.Thread):
    '''TODO'''
    _BREATH_TIMEOUT_SUCCESS = 1
    _BREATH_TIMEOUT_ERR = 10
    
    def __init__(self):
        threading.Thread.__init__(self)
        self.shutdown_flag = False
        
    def run(self):
        '''TODO'''
        while not self.shutdown_flag:
            try:
                if self.serve():
                    time.sleep(self._BREATH_TIMEOUT_SUCCESS)
                else:
                    time.sleep(self._BREATH_TIMEOUT_ERR)                
            except:
                # @todo: increase sleep time by error count
                time.sleep(self._BREATH_TIMEOUT_ERR)
                
                traceback.print_exception(*sys.exc_info(), file=sys.stdout)
                
    def serve(self):
        '''Subclass MUST override this method and put business logic here'''
        raise NotImplementedError()
                
    @classmethod
    def start_(cls, pidfile):
        ''''''
        if not _get_pid(pidfile):
            try:
                f = open(pidfile, 'w')
                f.write(str(os.getpid()))
                f.flush()
                # force SIGINT go to main thread
                signal.signal(signal.SIGINT, _interrupt_handler)
                
                worker = cls()
                worker.daemon = True
                worker.start()
                
                while 1 < threading.active_count(): # more threads than the main
                    time.sleep(0.1) # just waiting for KeyboardInterrupt...
            except KeyboardInterrupt:
                print 'shutting down...'
                    
                worker.shutdown_flag = True
                worker.join()
            except Exception as err:
                mail_admins('{} dead'.format(cls.__name__), err)
                raise  
            finally:
                f.close()
                os.remove(pidfile)
        else:
            print '{} is already running'.format(cls.__name__)            
            
    @classmethod
    def stop_(cls, pidfile):
        pid = _get_pid(pidfile)
        if pid:
            os.kill(pid, signal.SIGINT)
        else:
            print '{} is not running'.format(cls.__name__)