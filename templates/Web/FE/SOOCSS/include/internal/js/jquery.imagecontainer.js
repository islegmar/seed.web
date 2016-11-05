/**
 * Receives files dropped and build an Image object.
 * By default, put the image where it's dropped
 * 
 * Shows an image and we can draw over.
 * 
 * In some cases we want to do an image resizabe/draggable bu there is a bug:
 * http://bugs.jqueryui.com/ticket/4241
 * The solution is to put the image inside a div, and this is the reason for
 * the 'wrapOnDiv' option
 * 
 * IL - 07/02/14
 * Make this version 'clonable compatible' removing references to $el
 * 
 * A jQuery plugin boilerplate.
 * Author: Jonathan Nicol @f6design
 * http://f6design.com/journal/2012/05/06/a-jquery-plugin-boilerplate/
 */
;(function($) {
  // Change this to your plugin name.
  var pluginName = 'imagecontainer';
 
  /**
   * The element is the container that contains:
   * - A div that receives drop events for showing images
   */
  function Plugin(element, options) {
    // References to DOM and jQuery versions of element.
    var el = element;
    var $el = $(element);
 
    // Extend default options with those supplied by user.
    options = $.extend({
      /* Not used */
      'acceptedTypes' : ['image/png', 'image/jpeg', 'image/gif'],
      /* If true, the image is put where it was dropped */
      'putInPlace' : true, 
      /* Define a callback funtion that is called once the Image is created and
       * (it this is the case) after putInPlace is done
       */
      'onDrop' : null,
      /* Set the width for image */
      'imgWidth' : null,
      /* Set the height for the image */
      'imgHeight' : null,
      /* Put the image inside a div (see above for explanation) */
      'wrapOnDiv' : true ,
      /* Resize dimensions */
      'resize' : { width : 200, height : null}
    }, $.fn[pluginName].defaults, options);
    
    /**
     * Initialize plugin.
     */
    function init() {
      // Only has sense if we do something with the dropped
      if ( options.onDrop==null && !options.putInPlace ) return;
      
      // Without that, FF is not working and the dropped image is shown in the 
      // browser (default behaviour)
      $el.on('dragover', function(e) {
        if (e.stopPropagation) { e.stopPropagation(); } // The if checks are excessive but safest
        if (e.preventDefault) { e.preventDefault(); }
      });
      
      // When receives a file, show it if it is an image
      //--- el.addEventListener("drop", function(originalEvent){
      //---   console.log('imageContainer> drop image');
        
      //--- var dropEvent = originalEvent;
      $el.on('drop', function( dropEvent) {
        var $originalEl = $(this);
        
        // Original event
        var originalEvent = dropEvent.originalEvent;
        // stop the browser from opening the file
        dropEvent.preventDefault();
        
        // When dropping an image, content for originalEvent.dataTransfer.types[] 
        // and the fields 
        // - type : originalEvent.dataTransfer.types[ind]
        // - data : originalEvent.dataTransfer.getData(type)
        // We perform two tests: 
        // - Drop a file from file system
        // - Drop an image from another web page
        
        // [Chrome]
        // Image from another page
        // - [0] type : text/html, data : <img border="0" alt="WhatsApp rompe 28 millones de parejas" width="273" height="180" id="mod140779ale_0_img" src="http://www.cadenaser.com/prom/201310/pro_photo1381148419.jpg">
        // - [1] type : text/uri-list, data : http://www.cadenaser.com/tecnologia/articulo/whatsapp-rompe-28-millones-parejas/csrcsrpor/20131007csrcsrtec_1/Tes
        //
        // A file from file system
        // - [0] type : Files, data : 
        //
        // [Firefox]
        // Image from another page
        // - [0] type : text/html,      data : <chinese characters> -> Is it maybe the image?
        // - [1] type : text/x-moz-url, data : http://www.cadenaser.com/tecnologia/articulo/whatsapp-rompe-28-millones-parejas/csrcsrpor/20131007csrcsrtec_1/Tes
        //
        // A file from file system
        // - [0] type : application/x-moz-file, data : 
        // - [1] type : text/x-moz-url,         data : file:///home/islegmar/fotos/test.jpg
        // - [2] type : text/plain,             data : file:///home/islegmar/fotos/test.jpg
        // - [3] type : Files,                  data : 
        
        for(var ind=0; ind<originalEvent.dataTransfer.types.length; ++ind) {
          var type = originalEvent.dataTransfer.types[ind];
          var data = originalEvent.dataTransfer.getData(type);
          /*
          if ( type=='text/html' ) {
            $.post(
                'http://local.issi4u.com/kidSiteBuilding/service/UploadFile',
                {
                  image : data
                },
                function(data) {
                  alert("Ipload done : " + data.Url);
                } 
            );
          }
          */
        }
        
        /*
        if ( originalEvent.dataTransfer.items ) {
          alert("NEW Dropped " + originalEvent.dataTransfer.items.length + " items.");
          for(var ind=0; ind<originalEvent.dataTransfer.items.length; ++ind) {
            var item = originalEvent.dataTransfer.items[ind];
            alert("Item " + ind + "> kind : " + item.kind + ", type : " + item.kind);
            item.getAsString(function(content){
              alert("getAsString : " + content);
            });
          }
        }
        */  
        // If we have not dropped a file,do nothing
        if ( !originalEvent.dataTransfer ||
             !originalEvent.dataTransfer.files || 
              originalEvent.dataTransfer.files.length!=1 ) {
          return;
        }
        
        // Get the file
        var file = originalEvent.dataTransfer.files[0];
        // Get the coordinates where this event took place
        var position = {
            x : originalEvent.clientX,
            y : originalEvent.clientY
        };
        
        // Resize the image
        if ( options.resize ) {
          var reader = new FileReader();
          reader.onloadend = function() {
            var tempImg = new Image();
            tempImg.src = reader.result;
            tempImg.onload = function() {
              // ----------------------------------- Calculate the new dimesions
              // This are the actual dimensions of the image
              var originalW = tempImg.width;
              var originalH = tempImg.height;
              // Now we want to calculate the new dimensions
              var newW = options.resize.width;
              var newH = options.resize.height;
              
              // If only one dimension is specified, we have to scale
              if ( !newH ) {
                newH = originalH*newW/originalW;
              } else if ( !newW ) {
                newW = originalW*newH/originalH;
              }
              console.log('newW : ' + newW + ', newH : ' + newH);  
              
              // ---------------------------------------------- Draw in a canvas
              var canvas = document.createElement('canvas');
              canvas.width = newW;
              canvas.height = newH;
              var ctx = canvas.getContext("2d");
              ctx.drawImage(this, 0, 0, newW, newH);
              
              var imageResized = new Image();
              imageResized.src = canvas.toDataURL("image/png");
              // IL - 07/02/14 - Not use $el to make this plugin clonable resistant
              processImage(imageResized, position, dropEvent, $originalEl);

              /*
              The Original resize code (por si las flies!)
              var MAX_WIDTH = 400;
              var MAX_HEIGHT = 300;
              var tempW = tempImg.width;
              var tempH = tempImg.height;
              if (tempW > tempH) {
                  if (tempW > MAX_WIDTH) {
                     tempH *= MAX_WIDTH / tempW;
                     tempW = MAX_WIDTH;
                  }
              } else {
                  if (tempH > MAX_HEIGHT) {
                     tempW *= MAX_HEIGHT / tempH;
                     tempH = MAX_HEIGHT;
                  }
              }
              
              var canvas = document.createElement('canvas');
              canvas.width = tempW;
              canvas.height = tempH;
              var ctx = canvas.getContext("2d");
              ctx.drawImage(this, 0, 0, tempW, tempH);
              var dataURL = canvas.toDataURL("image/jpeg");
              */
            } // onloadTempImage
          } // reader.onloadend
          reader.readAsDataURL(file);  
        
        // Not resize the image, just read the file  
        } else {
          var reader = new FileReader();
          reader.onload = function (event) {
            var image = new Image();
            image.src = event.target.result;
            // IL - 07/02/14 - Not use $el to make this plugin clonable resistant
            processImage(image, position, dropEvent, $originalEl);
          };
          reader.readAsDataURL(file);
        }
      //}});
      });
      
      hook('onInit');
    }
    
    
    /**
     * Destroy plugin.
     * Usage: $('#el').demoplugin('destroy');
     */
    function destroy() {
      // Iterate over each matching element.
      $el.each(function() {
        var el = this;
        var $el = $(this);
 
        // Add code to restore the element to its original state...
        
        hook('onDestroy');
        // Remove Plugin instance from the element.
        $el.removeData('plugin_' + pluginName);
      });
    }
    
    // --------------------------------------------------------- Private Methods
    /**
     * Process image. Receives an Image and process it.
     * IL - 07/02/14 - $el is received as argument (not use the global variable
     * to make this plugin 'clonable resistant'
     */
    function processImage(image, position, dropEvent, $el) {
      var $image = $(image);
      
      // The element we're going to create
      var $newEle;
      
      // Wrap in a div
      if ( options.wrapOnDiv ) {
        $newEle = $('<div></div>');
        if ( options.imgWidth ) $newEle.width(options.imgWidth);
        if ( options.imgHeight ) $newEle.height(options.imgHeight);
        $image.css('width', '100%');
        $image.css('height', '100%');
        $newEle.append($image);
      // Just the image
      } else {
        if ( options.imgWidth ) image.width = options.imgWidth;
        if ( options.imgHeight ) image.height= options.imgHeight;
        $newEle = $image;
      }
      
      if ( options.putInPlace ) {
        putInPlace($newEle, position);
      }
      // IL - 30/10/13 - Added the $el argument
      if ( options.onDrop ) {
        options.onDrop($newEle, image, position, dropEvent, $el);
      }
    }
    
    /**
     * Default implementation that just put the image where it was dropped
     */
    function putInPlace($image, pos) {
      // Get the coordinates
      $image
        .css('position', 'absolute')
        .css('top', pos.y)
        .css('left', pos.x);
      $el.append($image);
    }
    
    // ---------------------------------------------------------- Public Methods
    

    // ------------------------------------------------------------ Common Stuff
    /**
     * Get/set a plugin option.
     * Get usage: $('#el').demoplugin('option', 'key');
     * Set usage: $('#el').demoplugin('option', 'key', value);
     */
    function option (key, val) {
      if (val) {
        options[key] = val;
      } else {
        return options[key];
      }
    }
 
    /**
     * Callback hooks.
     * Usage: In the defaults object specify a callback function:
     * hookName: function() {}
     * Then somewhere in the plugin trigger the callback:
     * hook('hookName');
     */
    function hook(hookName) {
      if (options[hookName] !== undefined) {
        // Call the user defined function.
        // Scope is set to the jQuery element we are operating on.
        options[hookName].call(el);
      }
    }
 
    // Initialize the plugin instance.
    init();
 
    // Expose methods of Plugin we wish to be public.
    return {
      option: option,
      destroy: destroy
    };
  }
 
  /**
   * Plugin definition.
   */
  $.fn[pluginName] = function(options) {
    // If the first parameter is a string, treat this as a call to
    // a public method.
    if (typeof arguments[0] === 'string') {
      var methodName = arguments[0];
      var args = Array.prototype.slice.call(arguments, 1);
      var returnVal;
      this.each(function() {
        // Check that the element has a plugin instance, and that
        // the requested public method exists.
        if ($.data(this, 'plugin_' + pluginName) && typeof $.data(this, 'plugin_' + pluginName)[methodName] === 'function') {
          // Call the method of the Plugin instance, and Pass it
          // the supplied arguments.
          returnVal = $.data(this, 'plugin_' + pluginName)[methodName].apply(this, args);
        } else {
          throw new Error('Method ' +  methodName + ' does not exist on jQuery.' + pluginName);
        }
      });
      if (returnVal !== undefined){
        // If the method returned a value, return the value.
        return returnVal;
      } else {
        // Otherwise, returning 'this' preserves chainability.
        return this;
      }
    // If the first parameter is an object (options), or was omitted,
    // instantiate a new instance of the plugin.
    } else if (typeof options === "object" || !options) {
      return this.each(function() {
        // Only allow the plugin to be instantiated once.
        if (!$.data(this, 'plugin_' + pluginName)) {
          // Pass options to Plugin constructor, and store Plugin
          // instance in the elements jQuery data object.
          $.data(this, 'plugin_' + pluginName, new Plugin(this, options));
        }
      });
    }
  };
 
  // Default plugin options.
  // Options can be overwritten when initializing plugin, by
  // passing an object literal, or after initialization:
  // $('#el').demoplugin('option', 'key', value);
  $.fn[pluginName].defaults = {
    onInit: function() {},
    onDestroy: function() {}
  };
 
})(jQuery);
