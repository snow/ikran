/**
 * namespace and basic
 * --------------------
 */
(function($){
    window.ikr = {};
    
    rcp.j_doc.one('ready', function(evt){
        ikr.j_imgls = $('.imgls');
    });
})(jQuery);

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
        
        PLACEHOLDER_URI = '/s/common/i/loading-31.gif',
        
        j_darkbox,
        j_db_hd,
        j_db_img,
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
        j_db_img = j_darkbox.find('img');
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
        on('click', function(evt){
            if(j_db_ft.is(':visible')){                
                j_db_ft.hide();
            } else {
                j_db_ft.show();
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
        var thumbs = j_db_thumbs.find('[imgid]');
        thumb_width = thumbs.outerWidth() + 
                      /\d+/.exec(j_db_thumbs.find('img').attr('width'))[0];
        var thumb_count = thumbs.length;
        
        j_db_thumbs.width(thumb_width * thumb_count);
        
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
        
        j_db_thumbs.find('[imgid]').length && init_thumbs();
    }
    
    rcp.j_doc.one('ready', init);
    
    function on_upload_done(evt, j_imgctn){
        add_thumb(j_imgctn, true);
    }
    
    function add_thumb(j_origin, prepend){
        var imgid = j_origin.attr('imgid');
        
        if(j_db_thumbs.find('[imgid='+imgid+']').length){
            return;
        }
        
        var j_thumb = j_db_thumb_tpl.clone();
        
        j_thumb.attr('imgid', imgid);
        j_thumb.find('img').attr('src', j_origin.attr('uri_ts'));   
        
        if(true === prepend){
            j_db_thumbs.prepend(j_thumb);
        } else {
            j_db_thumbs.append(j_thumb);
        }
        
        thumbls_initialized || init_thumbs();
        
        j_db_thumbs.width(thumb_width + j_db_thumbs.width());
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
    
    var PRELOAD_NEXT_LIMIT = 10;        
    function preload_next(j_thumb, depth){
        setTimeout(function(){
            var j_next = j_thumb.next('[imgid]');
            if(j_next.length){
                var origin = get_origin(j_next);
                rcp.preimg(origin.attr('uri_m'));
                
                depth += 1;
                if(depth < PRELOAD_NEXT_LIMIT){
                    preload_next(j_next, depth);
                }
            }
        }, 500);
    }
    
    var PRELOAD_PREV_LIMIT = 3;
    function preload_prev(j_thumb, depth){
        setTimeout(function(){
            var j_prev = j_thumb.prev('[imgid]');
            if(j_prev.length){
                var origin = get_origin(j_prev);
                rcp.preimg(origin.attr('uri_m'));
                
                depth += 1;
                if(depth < PRELOAD_NEXT_LIMIT){
                    preload_prev(j_prev, depth);
                }
            }
        }, 1000);
    }
    
    ikr.darkbox.show = function(j_imgctn){
        j_img = j_imgctn.find('img');
        
        j_db_img.one('load', function(evt){
            j_db_img.attr('src', j_imgctn.attr('uri_m'));
            j_db_img.attr('alt', j_img.attr('alt'));
            
            j_db_thumbs.find('.on').removeClass('on');
            var j_thumb = j_db_thumbs.find('[imgid='+j_imgctn.attr('imgid')+']')
            j_thumb.addClass('on');
            
            preload_next(j_thumb, 0);
            preload_prev(j_thumb, 0);
            
            j_surveymeter.appendTo($('body'));
            var offset = j_surveymeter.offset();
            j_surveymeter.detach();
            
            thumb_target_left = offset.left - j_thumb.outerWidth() / 2;
            thumb_cur_left = j_thumb.offset().left;
            list_cur_left = j_db_thumbs.offset().left;
            j_db_thumbs.css(
                'left', list_cur_left + (thumb_target_left - thumb_cur_left));
        });
        
        j_db_img.attr('src', PLACEHOLDER_URI);
        
        if(!is_shown){
            j_darkbox.fadeIn();
            j_darkbox.css('display', 'table');
            is_shown = true;
        }
    };
    
    ikr.darkbox.hide = function(){
        j_darkbox.fadeOut();
        is_shown = false;
    }
})(jQuery);

/**
 * image list
 * --------------------
 */
(function($){
    ikr.imgls = {};
    
    var j_imgctn_tpl, j_meta_tpl,
        initialized = false;
        
    function init(){
        if(initialized){return;}
        
        j_imgctn_tpl = ikr.j_imgls.find('.imgctn.tpl').remove().removeClass('tpl');
        j_meta_tpl = j_imgctn_tpl.find('.meta.tpl').remove().removeClass('tpl');
        //rcp.l(ikr.j_imgls);
        //rcp.l(ikr.j_imgls.find('.imgctn.tpl'));
        
        initialized = true;
        /*rcp.l(function(){
            var count = 0;
            
            j_imgctn_tpl.length && (count++);
            j_meta_tpl.length && (count++);
            
            return '[imgls] init done {}/2'.replace('{}', count);
        });*/
    }
    
    ikr.imgls.add_img = function(src, status, meta, append){
        init();
        
        var j_imgctn = j_imgctn_tpl.clone().addClass(status);
            
        j_imgctn.find('img').attr('src', src);
        j_imgctn.find('.status').text(status);
        
        if('object' === typeof meta){
            var caption = j_imgctn.find('figcaption');
            $.each(meta, function(key, value){
                var j_meta = caption.find('.'+key);
                
                if(0===j_meta.length){
                    j_meta = j_meta_tpl.clone().addClass(key).appendTo(caption);
                }
                
                if('size' === key){
                    j_meta.attr('extract', value);
                    j_meta.text(Math.round(value / 1024 / 1024 * 100) / 100 
                                + 'mb')
                } else {
                    j_meta.text(value);
                }
            });
        }
        
        if(true === append){
            j_imgctn.appendTo(ikr.j_imgls);
        } else {
            j_imgctn.prependTo(ikr.j_imgls);
        }
    }
})(jQuery);

/**
 * uploading img
 */
(function($){
    ikr.upload = {};
    
    settings = {
        SELECT_FILE_BTN_CLASS: 'selectfile',
        SELECT_FILE_BTN_TXT: 'Select local files',
        SELECT_FILE_BTN_TPL: '<a class="{class}" href="#">{txt}</a>',
        
        MASK_TPL: '<div class="dropzone">'+
                '<div class="bg"></div>'+
                '<div class="inr">drop files here</div>'+
            '</div>',
    };
    
    ikr.upload.config = function(options){
        $.extend(settings, options);
    };
    
    ikr.upload.enhanceform = function(field, autosubmit, hidesubmit, btntpl){
        // get reference to the field
        var j_field;
        if(field && 'string' === typeof field){
            j_field = $(field);
        } else if('object' === typeof field) {
            j_field = field;
        }
        
        // hide field and put trigger anchor
        var tpl;
        if(btntpl && 'string' === typeof btntpl){
            tpl = btntpl;
        } else {
            tpl = settings.SELECT_FILE_BTN_TPL;
            tpl = tpl.replace('{class}', settings.SELECT_FILE_BTN_CLASS);
            tpl = tpl.replace('{txt}', settings.SELECT_FILE_BTN_TXT);
        }
        
        // this class make file filed poistion:absolute and opacity:0
        // to overlap select link
        // doesnt user like to trigger click event on file filed
        // as this may not work due to browser security policy
        j_field.wrap('<div class="wrap" />');
        j_link = $(tpl).insertAfter(j_field);
        
        // auto submit
        if(false !== autosubmit){
            var j_form = j_field.closest('form');
            j_field.on('change', function(evt){
                queue_images(evt.target.files, evt.timeStamp);
                return false;
            });
            
            if(false !== hidesubmit){
                j_form.find('[type=submit]').hide();
            }
        }
    };
    
    var is_drag_evt_handled = false,
    
        j_mask,
        j_inr,
        j_retrytpl = $('<a class="retry" href=#>retry</a>'),
        
        API_UPLOAD_URI = '/api/img/uploadraw/?filename={filename}',
        MAX_UPLOAD_CONN = 2,
        
        cur_upload_conn = 0,
        files_to_upload = {};
        
    ikr.upload.E_UPLOAD_START = 'evt-ikr-upload_start';
    ikr.upload.E_UPLOAD_DONE = 'evt-ikr-upload_done';  
        
    rcp.preimg('/s/common/i/loading-16.gif');
    rcp.preimg('/s/common/i/alert-16.png');
    
    function init_dnd(){
        j_mask = $(settings.MASK_TPL);
        j_inr = j_mask.find('.inr');
        
        rcp.j_doc.on({
            'dragover': on_drag_over,
            'drop': on_drop,
            'keydown': function(evt){
                (27 === evt.which) && after_drop();
            }
        });
        
        rcp.j_doc.on('click', 'body>.dropzone', after_drop);
        ikr.j_imgls.on(ikr.upload.E_UPLOAD_START, on_upload_start);
        ikr.j_imgls.on(ikr.upload.E_UPLOAD_DONE, on_upload_start);
        ikr.j_imgls.on('click', '.retry', on_retry);
    }
    
    rcp.j_doc.one('ready', init_dnd);
    
    function on_drag_over(evt){
        if(!is_drag_evt_handled){
            is_drag_evt_handled = true;     
            
            evt.originalEvent.dataTransfer.dropEffect = 'copy';
            
            $('body').append(j_mask);
            j_inr.width(j_mask.width() - 
                         (j_inr.outerWidth() - j_inr.width()));
            j_inr.height(j_mask.height() - 
                          (j_inr.outerHeight() - j_inr.height()));   
        }
        return false;
    }
    
    function on_drop(evt){
        evt.preventDefault();
        queue_images(evt.originalEvent.dataTransfer.files, evt.timeStamp);
        
        after_drop();
        return false;
    }
    
    function after_drop(){
        j_mask.detach();
        is_drag_evt_handled = false;
    }
    
    function queue_images(filelist, timestamp){
        $.each(filelist, function(idx, file){
            if(/^image.(jpeg|png|gif)/.test(file.type)){
                var reader = new FileReader(),
                    filename = file.name,
                    id = timestamp + '-' + idx;
                
                files_to_upload[id] = file;
                    
                reader.onload = function(evt){
                    ikr.imgls.add_img(evt.target.result, 'queue', {
                        'title': filename,
                        'size': file.size,
                        'file_id': id
                    });
                    
                    ikr.j_imgls.trigger(ikr.upload.E_UPLOAD_START);
                }
                
                reader.readAsDataURL(file);
            }
        });
        
        ikr.j_imgls.find('.empty').remove();
    }
        
    function on_upload_start(evt){
        while(cur_upload_conn < MAX_UPLOAD_CONN){
            var j_imgctn = ikr.j_imgls.find('.imgctn.queue:first');
            
            if(j_imgctn.length){
                upload_file(j_imgctn);
            } else {
                break;
            }
        }
    }
    
    function upload_file(j_imgctn){
        var id = j_imgctn.find('.file_id').text(),
            filename = j_imgctn.find('.title').text(),
            file = files_to_upload[id];
            
        cur_upload_conn += 1;
        j_imgctn.removeClass('queue').addClass('ing').find('.status').empty();
        
        $.ajax(API_UPLOAD_URI.replace('{filename}', filename), {
            type: 'POST',
            data: file,
            processData: false,
            dataType: 'json',
            contentType: 'application/octet-stream',
            success: function(resp, textStatus, jqXHR){
                //rcp.l(resp);
                on_ajax_success(resp, j_imgctn);
                delete files_to_upload[id];
            },
            error: function(jqXHR, textStatus, errorThrown){
                on_ajax_error();
            },
            complete: function(){
                cur_upload_conn -= 1;
            }
        });
    }
    
    function on_ajax_success(resp, j_imgctn){
        j_imgctn.removeClass('ing').addClass('done');
        j_imgctn.find('.size').remove();
        j_imgctn.find('.status').empty();        
        
        j_imgctn.attr('imgid', resp.result.id).
                 attr('uri_m', resp.result.uri_m).
                 attr('uri_ts', resp.result.uri_ts);
        
        var j_img = j_imgctn.find('img');
        j_img.attr('src', resp.result.uri_s).
              attr('alt', resp.result.title);
              
        j_imgctn.find('.title').text(resp.result.title);
        j_imgctn.find('.desc').text(resp.result.desc);
        
        ikr.j_imgls.trigger(ikr.upload.E_UPLOAD_DONE, [j_imgctn]);
    }
    
    function on_ajax_error(j_imgctn){
        j_imgctn.removeClass('ing').addClass('err');
        j_imgctn.find('.status').empty();
        j_imgctn.find('.mask').append(j_retrytpl.clone());
    }
    
    function on_upload_done(evt){
        ikr.j_imgls.trigger(ikr.upload.E_UPLOAD_START);
    }
    
    function on_retry(evt){
        evt.preventDefault();
        
        var j_link = $(evt.target),
            j_imgctn = j_link.closest('.imgctn');
            
        j_imgctn.removeClass('err').addClass('queue');
        j_imgctn.find('.status').text('queue');
        j_link.remove();
        
        ikr.j_imgls.trigger(ikr.upload.E_UPLOAD_START);
        
        return false;
    }
})(jQuery);
