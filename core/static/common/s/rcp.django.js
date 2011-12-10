/**
 * namespace and basic
 * --------------------
 */
(function($){
    window.rcp.django = {}
})(jQuery);

/**
 * csrf
 */
(function($){
    function safeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    
    rcp.j_doc.ajaxSend(function(evt, xhr, settings) {
        if (!safeMethod(settings.type) && !settings.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", $.cookie('csrftoken'));
        }
    });
})(jQuery);
