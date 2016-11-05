/**
 * Put it over a website, allows to maminuplate the original web site contents.
 * 
 * A jQuery plugin boilerplate.
 * Author: Jonathan Nicol @f6design
 * http://f6design.com/journal/2012/05/06/a-jquery-plugin-boilerplate/
 */
;(function($) {
  // Change this to your plugin name.
  var pluginName = 'websitecontainer';
 
  /**
   * The element is the container that contains:
   * - A div that receives drop events for showing images
   */
  function Plugin(element, options) {
    
    // References to DOM and jQuery versions of element.
    var el = element;
    var $el = $(element);
    var webSiteContainer  = null;
    var $webSiteContainer = null;
    var lastUrl=null;
    // Represents the included web site
    var $iframe = null;
    var iframe = null;
    var $webSiteDocument = null;
    var $webSiteBody     = null;
 
    // Extend default options with those supplied by user.
    options = $.extend({
      /*$container  : $('#container'),
      iframe      : $('#site').get(0),*/
      $webSiteContainer : null,
      $iframe      : null,
      captureMouseEvents : null,
      fWhenLoaded : null
    }, $.fn[pluginName].defaults, options);
    
    /**
     * Initialize plugin.
     */
    function init() {
      // Primero obtenemos el webSiteCOntainer. Puede ser 'el' (lo que quiere 
      // decir que el iframe es un hijo) o un elemento externo
      //$CONTAINER = $('#container');
      //IFRAME = document.getElementById('site');
      
      // First check if we have set explicity those variables
      $webSiteContainer = options.$webSiteContainer;
      $iframe           = options.$iframe;

      // Now, try to guess it!
      if ( $webSiteContainer==null && !$el.is('iframe') ) {
        $webSiteContainer=$el;
      }
      if ( $iframe==null && $el.is('iframe') ) {
        $iframe=$el;            
      } 
      if ( $iframe==null && $webSiteContainer!=null ) {
        $iframe=$webSiteContainer.find('iframe');            
      } 

      
      if ( options.captureMouseEvents!=null ) {
        if ( options.captureMouseEvents )  {
          captureMouseEvents();
        } else {
          ignoreMouseEvents();
        }
      }
      
      // Utilities
      if ( $webSiteContainer!=null ) {
        webSiteContainer=$webSiteContainer.get(0);
      }
      if ( $iframe!=null ) {
        iframe=$iframe.get(0);
      }      
      

      // If no iframe, just return
      if (!iframe ) {
        if ( options.fWhenLoaded ) {
          options.fWhenLoaded();
        }
      // If we have an iframe, wait until it is loaded
      } else {
        $(iframe).bind('load',function(){
          var idoc=(this.contentWindow || this.contentDocument);
          if (idoc.document) {
            idoc=idoc.document;
          }
          $webSiteDocument= $(idoc);
          // Es raro, pero es la manera de acceder para haccer triggers ¿¿??
          // Se intenta de otras maneras ($SITE.find("body")) pero no hay forma
          // http://stackoverflow.com/questions/4101457/access-jquery-data-from-iframe-element
          //      You need to get the cache element from that window's jQuery object, like this:
          //
          //      var windowjQuery = $('#frame')[0].contentWindow.$;
          //      var f = $('#frame').contents().find('#data');
          //      Then to get data, use $.data(), like this:
          //
          //      windowjQuery.data(f[0], 'test1')
          //      What this is really accessing is:
          //
          //
          //      var key = f[0][frame.contentWindow.$.expando];
          //      var dataItem = frame.contentWindow.$.cache[key]["dataKey"];
          //$webSiteBody=$(iframe)[0].contentWindow.$('body');
          $webSiteBody=$iframe[0].contentWindow.$('body');
          
          /** Move the container as the site scrolls */
          //@todo: when changing page, if $SITE object changes, should the previous
          //event listener be removed?
          $webSiteDocument.scroll(function(evt){
            // Get how much has changed
            var topOffset = $webSiteDocument.find("body").scrollTop();
            // Move the container
            moveContainer(-topOffset);
          });
          
          // Fires an event: the show can start!!
          if ( options.fWhenLoaded ) {
            options.fWhenLoaded($webSiteContainer, $webSiteBody);
          }
        });
      }
      
      
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
     * Create a panel over another object
     */
    function createOver($obj, $reference, $whereToPut) {
      $obj.
           css("position","absolute").
           css("top"   ,$reference.offset().top).
           css("left"  ,$reference.offset().left).
           css("width" ,$reference.width()).
           css("height",$reference.height());
           //draggable();
      if ( $whereToPut ) {
        $whereToPut.append($obj);
      } else if ( $webSiteContainer!=null ) {
        $webSiteContainer.append($obj);
      }
      
      return $obj;
    }

    // Clon an object, put it on container a say goodbay to the original
    function clone(obj, addInsidePanel, $whereToPut) {
      var $obj = $(obj);
      var $newElement=null;
      
      if ( addInsidePanel ) {
        $newElement=$("<div></div>");
        $newElement.append($(obj.cloneNode(true)));
      } else {
        $newElement=$(obj.cloneNode(true));
      }
      
      $newElement.
           css("position","absolute").
           css("top"   ,$obj.offset().top  - $obj.scrollTop()).
           css("left"  ,$obj.offset().left - $obj.scrollLeft() ).
           css("width" ,$obj.width()).
           css("height",$obj.height());

      if ( $whereToPut ) {
        $whereToPut.append($newElement);
      } else if ( $webSiteContainer!=null ) {
        $webSiteContainer.append($newElement);
      }

      $obj.hide();
      
      return $newElement;
    }
    
    function getRandom(from,to) {
        return Math.floor(Math.random()*(to-from+1)+from);
    }

    

    /**
     * Check if the site url changes. We can not wait until the load event because
     * if the iframe can take too long for loading, so we perform periodic checks.
     */ 
    function listenOnSiteUrlChange(fCallback) {
      if ( !fCallback ) return;
      
      setInterval(
        function(){
          // iDoc changes when iframe is reloaded?
          var idoc=(iframe.contentWindow || iframe.contentDocument);
          if (idoc.document) {
            idoc=idoc.document;
          }
        
          var nowUrl = idoc.location.href;
          if ( lastUrl==null ) {
            lastUrl = nowUrl;
          } else if ( lastUrl!=nowUrl ) {
            lastUrl = nowUrl;
            fCallback(nowUrl);
          }
        },100);
    }

    function loadFrame($iframe, fWhenLoaded) {
      $iframe.bind('load',{fWhenLoaded:fWhenLoaded}, function(event){
        var fWhenLoaded = event.data.fWhenLoaded;
        if ( fWhenLoaded ) {
          var idoc=(this.contentWindow || this.contentDocument);
          if (idoc.document) {
            idoc=idoc.document;
          }
          var $body=$iframe[0].contentWindow.$('body');

          fWhenLoaded($(idoc), $(this), $body);
        }
      });
    }

    function loadUrl(url, fWhenLoaded) {
      var $iframe=$('<iframe src="' + url + '" ></iframe>').hide();
      $(document.body).append($iframe);
      loadFrame($iframe, function ($document,$iframe, $body){
        fWhenLoaded($document,$iframe, $body);
        $iframe.remove();
      });
    }

    // ---------------------------------------------------------- Public Methods
    /** Skip all mouse events */
    function ignoreMouseEvents() {
      if ( $webSiteContainer==null ) return;

      $webSiteContainer.css("pointer-events", "none");
    }

    /** Get all mouse events */
    function captureMouseEvents() {   
      if ( $webSiteContainer==null ) return;
      
      $webSiteContainer.css("pointer-events", "all");
    }

    /**
     * Move CONTAINER
     */
    function moveContainer(newPos){
      if ( $webSiteContainer==null ) return;

      $webSiteContainer.css("top", newPos);
    }

    function clean() {
      if ( $webSiteContainer==null ) return;

      $webSiteContainer.html('');
    }

    function appendElement($ele) {
      if ( $webSiteContainer==null ) return;

      $webSiteContainer.append($ele);
    }
    
    function getWebSiteBody() {   
      return $webSiteBody;
    }

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
      createOver : createOver
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
