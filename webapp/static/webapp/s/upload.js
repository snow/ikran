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
            
        ALBUM_ID: 0
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
        
        API_UPLOAD_URI = '/api/img/uploadraw/'+
                         '?filename={filename}&album_id={album_id}',
        MAX_UPLOAD_CONN = 2,
        ORIGIN_MASK_OPACITY = false,
        
        cur_upload_conn = 0,
        files_to_upload = {};
        
    ikr.upload.E_UPLOAD_START = 'evt-ikr-upload_start';
    ikr.upload.E_UPLOAD_DONE = 'evt-ikr-upload_done';  
        
    rcp.preimg('/s/common/i/loading-16.gif');
    rcp.preimg('/s/common/i/alert-16.png');
    
    ikr.upload.init_dnd = function(){
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
        
        $.ajax(API_UPLOAD_URI.replace('{filename}', filename).
                              replace('{album_id}', settings.ALBUM_ID), {
            type: 'POST',
            data: file,
            processData: false,
            dataType: 'json',
            contentType: 'application/octet-stream',
            xhr: function(){
                var xhr = new XMLHttpRequest(),
                    j_mask = j_imgctn.find('.mask'),
                    j_size = j_imgctn.find('.size');
                    
                xhr.upload.onprogress = function(evt){
                    if (evt.lengthComputable){
                        on_ajax_progress(j_mask, j_size, evt.loaded, evt.total);
                    }
                };
                return xhr;
            },
            success: function(resp, textStatus, jqXHR){
                //rcp.l(resp);
                on_ajax_success(resp, j_imgctn);
                delete files_to_upload[id];
            },
            error: function(xhr, textStatus, errorThrown){
                on_ajax_error(xhr, j_imgctn);
            },
            complete: function(){
                cur_upload_conn -= 1;
            }
        });
    }
    
    function on_ajax_progress(j_mask, j_size, loaded, total){
        if(!ORIGIN_MASK_OPACITY){
            ORIGIN_MASK_OPACITY = j_mask.css('opacity');
        }
        
        var opacity = Math.round(
                          ORIGIN_MASK_OPACITY * (total - loaded) / total * 10
                      ) / 10;
        if(opacity){
            j_mask.css('opacity', opacity);
        }
        
        j_size.text(ikr.byte2mb(loaded) + ' / ' + ikr.byte2mb(total) + ' mb');
    }
    
    function on_ajax_success(resp, j_imgctn){
        j_imgctn.removeClass('ing').addClass('done');
        j_imgctn.find('.size').remove();
        j_imgctn.find('.status').empty();        
        
        j_imgctn.attr('imgid', resp.result.id).
                 attr('uri_f', resp.result.uri_f).
                 attr('uri_ts', resp.result.uri_ts);
        
        var j_img = j_imgctn.find('img');
        j_img.attr('src', resp.result.uri_s).
              attr('alt', resp.result.title);
              
        j_imgctn.find('.title').text(resp.result.title);
        j_imgctn.find('.desc').text(resp.result.desc);
        
        ikr.j_imgls.trigger(ikr.upload.E_UPLOAD_DONE, [j_imgctn]);
    }
    
    function on_ajax_error(xhr, j_imgctn){
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
