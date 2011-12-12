/**
 * namespace and basic
 * --------------------
 */
(function($){
    window.ikr = {};
})(jQuery);

/**
 * darkbox
 * --------------------
 */
(function($){
    ikr.darkbox = {};
    
    var initialized = false,
        j_darkbox,
        j_dbimg;
        
    function init(){
        j_darkbox = $('.darkbox');
        j_dbimg = j_darkbox.find('img');
        initialized = true;
        
        rcp.j_doc.on('keydown', function(evt){
            (27===evt.which) && j_darkbox.fadeOut();
        });
    }
    
    ikr.darkbox.show = function(j_imgctn){
        if(!initialized){
            init();
        }
        
        j_img = j_imgctn.find('img');
        
        j_dbimg.attr('src', j_img.attr('uri_m'));
        j_dbimg.attr('alt', j_img.attr('alt'));
        j_dbimg.attr('width', j_img.attr('width_m'));
        j_dbimg.attr('height', j_img.attr('height_m'));
        
        j_darkbox.fadeIn();
        j_darkbox.css('display', 'table');
    };
})(jQuery);

/**
 * stream
 * --------------------
 */
(function($){
    ikr.stream = {};
    
    var j_imgls, j_imgctn_tpl, j_meta_tpl;
    function init(){
        j_imgls = $('.imgls');
        j_imgctn_tpl = j_imgls.find('.imgctn.tpl').remove().removeClass('tpl');
        j_meta_tpl = j_imgctn_tpl.find('.meta.tpl').remove().removeClass('tpl');
        
        j_imgls.on('click', '.view', function(evt)
        {
            ikr.darkbox.show($(evt.target).closest('.imgctn'));
            return false;
        });
    }
    
    ikr.stream.add_img = function(src, status, meta, append){
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
            j_imgctn.appendTo(j_imgls);
        } else {
            j_imgctn.prependTo(j_imgls);
        }
    }
    
    rcp.j_doc.ready(init);
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
        j_imgls,     
        j_retrytpl = $('<a class="retry" href=#>retry</a>'),
        
        API_UPLOAD_URI = '/api/img/uploadraw/?filename={filename}',
        MAX_UPLOAD_CONN = 2,
        E_UPLOAD_START = 'upload_start',
        E_UPLOAD_DONE = 'upload_done',
        cur_upload_conn = 0,
        files_to_upload = {};
        
    function on_upload_start(evt){
        while(cur_upload_conn < MAX_UPLOAD_CONN){
            var j_imgctn = j_imgls.find('.imgctn.queue:first');
            
            if(j_imgctn.length){
                upload_file(j_imgctn);
            } else {
                break;
            }
        }
    }
    
    function on_upload_done(evt){
        j_imgls.trigger(E_UPLOAD_START);
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
                j_imgctn.removeClass('ing').addClass('done');
                j_imgctn.find('.size').remove();
                j_imgctn.find('.status').empty();
                
                rcp.l(resp);
                
                var j_img = j_imgctn.find('img');
                j_img.attr('src', resp.result.uri_s).
                      attr('alt', resp.result.title).
                      attr('uri_m', resp.result.uri_m).
                      attr('uri_l', resp.result.uri_l).
                      attr('width', resp.result.width_s).
                      attr('height', resp.result.height_s).
                      attr('width_m', resp.result.width_m).
                      attr('height_m', resp.result.height_m).
                      attr('width_l', resp.result.width_l).
                      attr('height_l', resp.result.height_l);
                      
                j_imgctn.find('.title').text(resp.result.title);
                j_imgctn.find('.desc').text(resp.result.desc);
                
                delete files_to_upload[id];
                j_imgls.trigger(E_UPLOAD_DONE);
            },
            error: function(jqXHR, textStatus, errorThrown){
                j_imgctn.removeClass('ing').addClass('err');
                j_imgctn.find('.status').text('error');
                j_imgctn.find('.mask').append(j_retrytpl.clone());
            },
            complete: function(){
                cur_upload_conn -= 1;
            }
        });
    }
    
    function on_retry(evt){
        evt.preventDefault();
        
        var j_link = $(evt.target),
            j_imgctn = j_link.closest('.imgctn');
            
        j_imgctn.removeClass('err').addClass('queue');
        j_imgctn.find('.status').text('queue');
        j_link.remove();
        
        j_imgls.trigger(E_UPLOAD_START);
        
        return false;
    }
    
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
        
        return after_drop();
    }
    
    function after_drop(){
        j_mask.detach();
        is_drag_evt_handled = false;
        return false;
    }
    
    function queue_images(filelist, timestamp){
        $.each(filelist, function(idx, file){
            if(/^image.(jpeg|png|gif)/.test(file.type)){
                var reader = new FileReader(),
                    filename = file.name,
                    id = timestamp + '-' + idx;
                
                files_to_upload[id] = file;
                    
                reader.onload = function(evt){
                    ikr.stream.add_img(evt.target.result, 'queue', {
                        'title': filename,
                        'size': file.size,
                        'file_id': id
                    });
                    
                    j_imgls.trigger(E_UPLOAD_START);
                }
                
                reader.readAsDataURL(file);
            }
        });
    }
    
    function init_dnd(){
        j_mask = $(settings.MASK_TPL);
        j_inr = j_mask.find('.inr');
        j_imgls = $('.imgls');
        j_imgctn_tpl = j_imgls.find('.imgctn.tpl').remove().removeClass('tpl');
        
        rcp.j_doc.on({
            'dragover': on_drag_over,
            'drop': on_drop,
            'keydown': function(evt){
                (27 === evt.which) && after_drop();
            }
        });
        
        rcp.j_doc.on('click', 'body>.dropzone', after_drop);
        j_imgls.on(E_UPLOAD_START, on_upload_start);
        j_imgls.on(E_UPLOAD_DONE, on_upload_start);
        j_imgls.on('click', '.retry', on_retry);
    }
    
    rcp.j_doc.ready(init_dnd);
})(jQuery);
