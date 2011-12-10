/**
 * namespace and basic
 * --------------------
 */
(function($){
    window.ikr = {}
})(jQuery);

/**
 * modification to file uploader
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
        
        j_link = $(tpl).insertAfter(j_field);
        j_field.hide();
        
        j_link.click(function(evt){
            j_field.click();
            return false;
        });
        
        // auto submit
        if(false !== autosubmit){
            var j_form = j_field.closest('form');
            j_field.on('change', function(evt){
                j_form.submit();
            });
            
            if(false !== hidesubmit){
                j_form.find('[type=submit]').hide();
            }
        }
    };
    
    var is_drag_evt_handled = false,
        j_mask = false,
        j_inr = false;
        
    rcp.j_doc.on('ready', function(evt){
        rcp.j_doc.on({
            'dragover': function(evt){
                if(is_drag_evt_handled){
                    return false;
                } else {
                    is_drag_evt_handled = true;
                }
                
                evt.originalEvent.dataTransfer.dropEffect = 'copy';
                
                if(false === j_mask){
                    j_mask = $(settings.MASK_TPL);
                    j_inr = j_mask.find('.inr');
                } 
                
                $('body').append(j_mask);
                j_inr.width(j_mask.width() - 
                             (j_inr.outerWidth() - j_inr.width()));
                j_inr.height(j_mask.height() - 
                              (j_inr.outerHeight() - j_inr.height()));
                
                return false;
            },
            'drop': function(evt){
                evt.preventDefault();
                    
                $.each(evt.originalEvent.dataTransfer.files, function(idx, el){
                    var reader = new FileReader();
                    reader.onload = function(evt){
                        var dataurl = evt.target.result;
                        $('.imgls').prepend($('<img src="'+dataurl+'" />'));
                    }
                    
                    reader.readAsDataURL(el);
                });
                
                j_mask.detach();
                is_drag_evt_handled = false;
            },
            'keypress': function(evt){
                if(0 === evt.which){
                    if(j_mask){
                        j_mask.detach();                
                        is_drag_evt_handled = false;
                    }
                }
            }
        });
    });
    /*// override to add csrf token to request header
    qq.UploadHandlerXhr.prototype._upload = function(id, params){
        var file = this._files[id],
            name = this.getName(id),
            size = this.getSize(id);
                
        this._loaded[id] = 0;
                                
        var xhr = this._xhrs[id] = new XMLHttpRequest();
        var self = this;
                                        
        xhr.upload.onprogress = function(e){
            if (e.lengthComputable){
                self._loaded[id] = e.loaded;
                self._options.onProgress(id, name, e.loaded, e.total);
            }
        };

        xhr.onreadystatechange = function(){            
            if (xhr.readyState == 4){
                self._onComplete(id, xhr);                    
            }
        };

        // build query string
        params = params || {};
        params['filename'] = name;
        var queryString = qq.obj2url(params, this._options.action);

        xhr.open("POST", queryString, true);
        xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
        xhr.setRequestHeader("X-File-Name", encodeURIComponent(name));
        xhr.setRequestHeader("Content-Type", "application/octet-stream");
        // start mod 
        xhr.setRequestHeader("X-CSRFToken", $.cookie('csrftoken'));
        // end mod 
        xhr.send(file);
    };
    
    // override to handle html response
    qq.UploadHandlerXhr.prototype._onComplete = function(id, xhr){
        // the request was aborted/cancelled
        if (!this._files[id]) return;
        
        var name = this.getName(id);
        var size = this.getSize(id);
        
        this._options.onProgress(id, name, size, size);
                
        if (xhr.status == 200){
            this.log("xhr - server response received");
            this.log("responseText = " + xhr.responseText);
                        
            var response;
                    
            try {
                response = eval("(" + xhr.responseText + ")");
            } catch(err){
                response = {};
            }
            
            this._options.onComplete(id, name, response);
                        
        } else {                   
            this._options.onComplete(id, name, {});
        }
                
        this._files[id] = null;
        this._xhrs[id] = null;    
        this._dequeue(id);                    
    };
    
    qq.FileUploader.prototype._onComplete = function(id, fileName, result){
        qq.FileUploaderBasic.prototype._onComplete.apply(this, arguments);

        // mark completed
        var item = this._getItemByFileId(id);                
        qq.remove(this._find(item, 'cancel'));
        qq.remove(this._find(item, 'spinner'));
        
        if (result.success){
            qq.addClass(item, this._classes.success);    
        } else {
            qq.addClass(item, this._classes.fail);
        }         
    };*/
    
    /*ikr.upload.init = function(settings){
        return new qq.FileUploader($.extend(settings, {
            allowedExtensions: ['jpg', 'jpeg', 'png', 'gif'],
            sizeLimit: 10 * 1024 * 1024,   
            minSizeLimit: 10 * 1024
        }));
    };*/
})(jQuery);
