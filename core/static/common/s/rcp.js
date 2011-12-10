/**
 * namespace and basic
 * --------------------
 */
(function($){
    window.rcp = {
        j_doc: $(document)
    }
})(jQuery);

/**
 * logging
 * ---------
 */
(function($){
    rcp.l = function(){
        if(console){
            for(var i=0; i < arguments.length; i++){
                console.log(arguments[i]);
            }
        }
    };
})(jQuery);