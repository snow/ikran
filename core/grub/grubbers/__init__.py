import douban

list = {
    'www.douban.com': douban.DoubanPhotoGrubber
}

#_grubbers = {
#    'www.douban.com': douban.DoubanPhotoGrubber
#}
#
#def get(source):
#    ''''''
#    for domain in _grubbers.keys():                    
#        if source.startswith(domain):
#            return _grubbers[domain]
#        
#    raise Exception('could not find grubber for '+source)