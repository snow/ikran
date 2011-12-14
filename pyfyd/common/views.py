# Create your views here.

class AuthStartMixin(object):
    '''Provide common business logic in auth start'''
    def get_callback(self):
        '''expecting service pass back all query params'''
        if not self.callback:
            raise NotImplementedError('Subclass must provide oauth_callback')
        
        self.callback = '{}?{}'.format(self.callback, 
                                       self.request.GET.urlencode())
                        
        return self.callback
    
class AuthenticateReturnMixin(object):
    '''Provide common business logic in auth start'''
    def get_success_uri(self):
        '''handle django convernon 'next' and 'redirect_field_name' param'''
        get = self.request.GET
        
        if 'redirect_field_name' in get and get['redirect_field_name'] in get:
            return get[get['redirect_field_name']]
        elif 'next' in get:
            return get['next'] 
        elif self.success_uri:            
            return self.success_uri
        else:
            return False
