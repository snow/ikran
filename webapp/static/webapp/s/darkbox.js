/**
 * darkbox
 * --------------------
 */
(function($){
    ikr.darkbox = {};
    
    var is_shown = false,
        thumbls_initialized  = false,
        
        E_NEXT = 'evt-ikr-darkbox-next',
        E_PREV = 'evt-ikr-darkbox-prev',
        
        BREATH_TIMEOUT = 1500,
        
        PLACEHOLDER_URI = '/s/common/i/loading-31.gif',
        
        j_darkbox,
        j_db_hd,
        j_db_img,
        j_db_hd,
        j_db_ft,
        j_db_thumbs,
        j_db_thumb_tpl,
        j_surveymeter = $('<div id="darkbox-pgcenter-surveymeter" '+
            'style="position:fixed; top:50%; left:50%; width:0; height:0;" />'),
            
        thumb_width;
        
    rcp.preimg(PLACEHOLDER_URI);
    rcp.preimg('/s/common/i/view-40.png');
    rcp.preimg('/s/common/i/arrow-l-45_93.png');
    rcp.preimg('/s/common/i/arrow-r-45_93.png');
    
    function init_dom(){
        j_darkbox = $('.darkbox');
        j_db_hd = j_darkbox.find('header');
        j_db_img = j_darkbox.find('.bd').find('img');
        j_db_hd = j_darkbox.find('header');
        j_db_ft = j_darkbox.find('footer');
        j_db_thumbs = j_db_ft.find('.thumbs');
        j_db_thumb_tpl = j_db_thumbs.find('.thumb.tpl').remove().
                            removeClass('tpl');
                            
        /*rcp.l(function(){
            var count = 0;
            
            j_darkbox.length && (count++);
            j_db_hd.length && (count++);
            j_db_img.length && (count++);
            j_db_ft.length && (count++);
            j_db_thumbs.length && (count++);
            j_db_thumb_tpl.length && (count++);
            
            return '[darkbox] init dom {}/6'.replace('{}', count);
        });*/
       //rcp.l(rcp.j_doc.width(), rcp.j_doc.height());
       set_darkbox_size();
       
       $(window).on('resize', set_darkbox_size);
    }
    
    function init_evt(){
        j_darkbox.on('click', '.thumb', function(evt){
            ikr.darkbox.show(get_origin($(this)));
            return false;
        }).
        on('click', '.next', function(evt){
            j_darkbox.trigger(E_NEXT);
            return false;
        }).
        on('click', '.prev', function(evt){
            j_darkbox.trigger(E_PREV);
            return false;
        }).
        on('click', '.x', function(evt){
            ikr.darkbox.hide();
            return false;
        }).
        on('click', function(evt){
            // use display:none to hide element breaks center thumb function
            // as display:none elements dont have position
            if('visible' === j_db_ft.css('visibility')){
                j_db_hd.css('visibility', 'hidden');
                j_db_ft.css('visibility', 'hidden');
            } else {
                j_db_hd.css('visibility', 'visible');
                j_db_ft.css('visibility', 'visible');
            }
        }).
        on(E_NEXT, on_next).
        on(E_PREV, on_prev);
        
        ikr.j_imgls.on('click', '.view', function(evt)
        {
            ikr.darkbox.show($(evt.target).closest('.imgctn'));
            return false;
        });
        
        //rcp.debug() && rcp.l('[darkbox] init event');
    }
    
    function init_keyboard(){
        rcp.j_doc.on('keydown', function(evt){
            if(is_shown){
                switch(evt.which){
                case 27:
                    ikr.darkbox.hide();
                    break;
                    
                case 37: // left
                case 72: // h
                case 65: //a
                    j_darkbox.trigger(E_PREV);
                    break;
                    
                case 39: // right
                case 76: // l
                case 68: //d
                    j_darkbox.trigger(E_NEXT);
                    break;
                }
            }
        });
        
        //rcp.debug() && rcp.l('[darkbox] init keyboard');
    }
    
    function init_thumbs(){
        var j_thumb = j_db_thumbs.find('[imgid]:first');
            thumb_width = parseInt(j_thumb.outerWidth()) + 
                          parseInt(/\d+/.exec(j_thumb.find('img').attr('width'))[0]);            
                    
        //j_db_thumbs.width(thumb_width * thumbs.length);
        
        thumbls_initialized = true;
    }
        
    function init(){
        init_dom();
        init_evt();
        init_keyboard();
        
        var j_imgs = ikr.j_imgls.find('[imgid]');
            
        $.each(j_imgs, function(idx, el){
            var j_origin = $(el);
            add_thumb(j_origin);
        });
        //rcp.debug() && rcp.l('[darkbox] init done');
        
        ikr.j_imgls.on(ikr.upload.E_UPLOAD_DONE, on_upload_done);
        ikr.j_imgls.on(ikr.imgls.E_IMG_REMOVED, on_img_removed);
        ikr.j_imgls.on(ikr.imgls.E_IMG_LOADED, on_img_loaded);
        
        //j_db_thumbs.find('[imgid]').length && init_thumbs();
    }
    
    rcp.j_doc.one('ready', init);
    
    function set_darkbox_size(){
        j_db_img.css({
            'max-width': window.innerWidth,
            'max-height': window.innerHeight
        });
    }
    
    function on_upload_done(evt, j_imgctn){
        add_thumb(j_imgctn, true);
    }
    
    function on_img_removed(evt, j_2del){
        $.each(j_2del, function(idx, el){
            j_db_thumbs.find('[imgid='+$(el).attr('imgid')+']').remove();
        });
    }
    
    function on_img_loaded(evt, j_imgctn){
        add_thumb(j_imgctn, false);
    }
    
    function add_thumb(j_origin, prepend){
        var imgid = j_origin.attr('imgid');
        
        if(j_db_thumbs.find('[imgid='+imgid+']').length){
            return;
        }
        
        var j_thumb = j_db_thumb_tpl.clone();
        j_thumb.attr('imgid', imgid);
        
        if(true === prepend){
            j_db_thumbs.prepend(j_thumb);
        } else {
            j_db_thumbs.append(j_thumb);
        }
        
        thumbls_initialized || init_thumbs();
        j_db_thumbs.width(parseInt(thumb_width) + parseInt(j_db_thumbs.width()));
        
        j_thumb.find('img').attr('src', j_origin.attr('uri_ts'));
    }
    
    function on_next(evt){
        var j_t = get_origin(j_db_thumbs.find('.on').next('[imgid]'));
        j_t.length && ikr.darkbox.show(j_t);
    }
    
    function on_prev(evt){
        var j_t = get_origin(j_db_thumbs.find('.on').prev('[imgid]'));
        j_t.length && ikr.darkbox.show(j_t);
    }
    
        
    function get_origin(j_thumb){
        return $('.imgctn').filter('[imgid='+j_thumb.attr('imgid')+']');
    }
    
    var PRELOAD_NEXT_LIMIT = 5;        
    function preload_next(j_thumb, depth){
        setTimeout(function(){
            var j_next = j_thumb.next('[imgid]');
            if(j_next.length){
                var origin = get_origin(j_next);
                rcp.preimg(origin.attr('uri_f'));
                
                depth += 1;
                if(depth < PRELOAD_NEXT_LIMIT){
                    preload_next(j_next, depth);
                }
            }
        }, BREATH_TIMEOUT);
    }
    
    var PRELOAD_PREV_LIMIT = 2;
    function preload_prev(j_thumb, depth){
        setTimeout(function(){
            var j_prev = j_thumb.prev('[imgid]');
            if(j_prev.length){
                var origin = get_origin(j_prev);
                rcp.preimg(origin.attr('uri_f'));
                
                depth += 1;
                if(depth < PRELOAD_NEXT_LIMIT){
                    preload_prev(j_prev, depth);
                }
            }
        }, 2*BREATH_TIMEOUT);
    }
    
    function center_current_thumb(j_thumb){
        j_surveymeter.appendTo($('body'));
        var offset = j_surveymeter.offset();
        j_surveymeter.detach();
        
        thumb_target_left = offset.left - j_thumb.outerWidth() / 2;
        thumb_cur_left = j_thumb.offset().left;
        list_cur_left = j_db_thumbs.offset().left;
        j_db_thumbs.css(
            'left', list_cur_left + (thumb_target_left - thumb_cur_left)
        );
    }
    
    ikr.darkbox.show = function(j_imgctn){
        j_img = j_imgctn.find('img');
        
        j_db_img.attr('src', PLACEHOLDER_URI);
        
        j_db_img.attr('src', j_imgctn.attr('uri_f'));
        j_db_img.attr('alt', j_img.attr('alt'));
        
        j_db_thumbs.find('.on').removeClass('on');
        var j_thumb = j_db_thumbs.find('[imgid='+j_imgctn.attr('imgid')+']')
        j_thumb.addClass('on');
        
        preload_next(j_thumb, 0);
        preload_prev(j_thumb, 0);
        
        if(!is_shown){
            j_darkbox.fadeIn(function(){
                center_current_thumb(j_thumb);
            });
            j_darkbox.css('display', 'table');
            is_shown = true;
        } else {
            center_current_thumb(j_thumb);
        }
        
        if(5 > j_thumb.nextAll('[imgid]').length){
            ikr.j_imgls.trigger(ikr.imgls.E_LOADMORE);
        }
    };
    
    ikr.darkbox.hide = function(){
        is_shown = false;
        j_darkbox.fadeOut();
        
    }
})(jQuery);