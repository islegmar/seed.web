/**
 * Photo holder. Reveives dragged images.
 * ONLY store one image.
 * 
 * @see http://html5demos.com/dnd-upload
 * 
 * A jQuery plugin boilerplate.
 * Author: Jonathan Nicol @f6design
 * http://f6design.com/journal/2012/05/06/a-jquery-plugin-boilerplate/
 */
;(function($) {
  // Change this to your plugin name.
  var pluginName = 'photoholder';
 
  /**
   * Plugin object constructor.
   * Implements the Revealing Module Pattern.
   */
  function Plugin(element, options) {
    console.log("****** Plugin");
    
    // References to DOM and jQuery versions of element.
    var el = element;
    var $el = $(element);
 
    // Extend default options with those supplied by user.
    options = $.extend({
      'singleFile' : false,
      'autoSubmit' : false,
      'submitURL'  : null
    }, $.fn[pluginName].defaults, options);
    
    var holder = $el.find(".holder").get(0);
    var theFile = null;
    
    // Some initializations
    var tests = {
      filereader: typeof FileReader != 'undefined',
      dnd: 'draggable' in document.createElement('span'),
      formdata: !!window.FormData,
      progress: "upload" in new XMLHttpRequest
    };
    var support = {
      filereader: $el.find('.filereader').get(0),
      formdata: $el.find('.formdata').get(0),
      progress: $el.find('.progress').get(0)
    };
    var acceptedTypes = {
      'image/png': true,
      'image/jpeg': true,
      'image/gif': true
    };
    var progress = $el.find('.uploadprogress').get(0);
    var fileupload = $el.find('.upload').get(0);
    // @todo : check the init and use of this variable
    var formData = null;
    
    "filereader formdata progress".split(' ').forEach(function (api) {
      if (tests[api] === false) {
        support[api].addclassName = 'fail';
      } else {
        // FFS. I could have done el.hidden = true, but IE doesn't support
        // hidden, so I tried to create a polyfill that would extend the
        // Element.prototype, but then IE10 doesn't even give me access
        // to the Element object. Brilliant.
        support[api].className = 'hidden';
      }
    });
 
    /**
     * Initialize plugin.
     */
    function init() {
      console.log("****** init");
      
      // Receives dragged images, only if it supports
      if (tests.dnd) { 
        console.log('holder : ' + holder);
        holder.ondragover = function () { 
          console.log('Drag over');
          $(this).addClass('hover'); 
          return false;
        };
        holder.ondragend = function () { 
          $(this).removeClass('hover'); 
          return false; 
        };
        holder.ondrop = function (e) {
          $(this).removeClass('hover');
          e.preventDefault();
          readfiles(e.dataTransfer.files);
        }
      } else {
        console.log('***** tests.dnd : false');
        fileupload.className = 'hidden';
        fileupload.querySelector('input').onchange = function () {
          readfiles(this.files);
        };
      }
      
      /*
      if ( tests.formdata ) {
        formData = new FormData();
      }*/
      
      hook('onInit');
    }
    
    /**
     * Read files. It only read one (we could read more than one but then 
     * we could have other problems)
     */
    function readfiles(files) {
      if ( !files || files.length==0 ) return;
      
      var file = files[0];
      formData = new FormData();
      formData.append('file', file);
      previewfile(file, true);
      
      theFile = file;
    }
    
    /**
     * Preview file
     */
    function previewfile(file, cleanFirst) {
      if ( cleanFirst ) {
        $(holder).html('');
      }
      
      if (tests.filereader === true && acceptedTypes[file.type] === true) {
        var reader = new FileReader();
        reader.onload = function (event) {
          var image = new Image();
          image.src = event.target.result;
          image.width = 250; // a fake resize
          holder.appendChild(image);
        };

        reader.readAsDataURL(file);
      }  else {
        holder.innerHTML += '<p>Uploaded ' + file.name + ' ' + (file.size ? (file.size/1024|0) + 'K' : '');
        console.log(file);
      }
    }
    
    /**
     * Resize an upload a file
     */
    function resizeAndUpload(url, file, onEnd) {
      alert('resizeAndUpload');
      var reader = new FileReader();
      reader.onloadend = function() {
        var tempImg = new Image();
        tempImg.src = reader.result;
        tempImg.onload = function() {
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
   
          /*
          var xhr = new XMLHttpRequest();
          xhr.onreadystatechange = function(ev){
              //document.getElementById('filesInfo').innerHTML = 'Done!';
              alert("Imagen guardada!");
              if ( onEnd ) {
                onEnd('');
              }
          };
   
          xhr.open('POST', url, true);
          xhr.setRequestHeader("Content-type","application/x-www-form-urlencoded");
          var data = 'image=' + dataURL;
          xhr.send(data);
          */
          
          console.log('dataURL : ' + dataURL);
          var data = 'image=' + dataURL;
          $.post(url, {image:dataURL},function(data){
            if ( onEnd ) {
              onEnd(data);
            }
          });
          /*
          $.ajax({
            url: url,
            data: {
              'image' : dataURL
            },
            cache: false,
            contentType: false,
            processData: false,
            type: 'POST',
            async: false,
            success: function(data){
              if ( onEnd ) {
                onEnd(data);
              }
            }
          });
          */
        }
      } // reader.onloadend
      reader.readAsDataURL(file);
    } // resizeAndUpload
    
    /**
     * Upload All Files
     */
    function uploadFiles(url,onEnd) {
      console.log('>>>> on function uploadFiles');
      if ( formData ) {
        /*
        var xhr = new XMLHttpRequest();
        xhr.open('POST', options.submitURL);
        xhr.onload = function() {
          progress.value = progress.innerHTML = 100;
        };
        
        if (tests.progress) {
          xhr.upload.onprogress = function (event) {
            if (event.lengthComputable) {
              var complete = (event.loaded / event.total * 100 | 0);
              progress.value = progress.innerHTML = complete;
            }
          }
        }
        
        xhr.send(formData);
        */
        // IMPORTANT : CALL IS SYNCH to avoid problems when uploading in paralel
        // several files in the server
        resizeAndUpload(url, theFile, onEnd);
        /*
        console.log('>>> using jquery');
        $.ajax({
          url: url,
          data: formData,
          cache: false,
          contentType: false,
          processData: false,
          type: 'POST',
          async: false,
          success: function(data){
            if ( onEnd ) {
              onEnd(data);
            }
          }
        });
        */
        console.log('Uploaded');
      } else {
        if ( onEnd ) {
          onEnd(null);
        }
      }
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
      destroy: destroy,
      uploadFiles : uploadFiles
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
