/**
 * Create a mosaic distributing a serie of panels
 * 
 * A jQuery plugin boilerplate.
 * Author: Jonathan Nicol @f6design
 * http://f6design.com/journal/2012/05/06/a-jquery-plugin-boilerplate/
 */
;(function($) {
  // Change this to your plugin name.
  var pluginName = 'mosaicBuilder';
  
  /**
   * Plugin object constructor.
   * Implements the Revealing Module Pattern.
   */
  function Plugin(element, options) {
    // References to DOM and jQuery versions of element.
    // We want to be able to 'copy' this plugin when clone, so don't use those
    // general references
    var el = element;
    var $el = $(element);
    
    // Extend default options with those supplied by user.
    options = $.extend({
      'numCols'  : 3,
      'createGaps' : true,
      '$panels'  : null
    }, $.fn[pluginName].defaults, options);
    var $columns = new Array(options.numCols);

    /**
     * Initialize plugin.
     */
    function init() {
      // Create the columns
      for(var ind=0; ind<options.numCols; ++ind){
        $columns[ind] = $('<div></div>');
        $el.append($columns[ind]);
      }

      // Distribute the divs in the columns
      for(var ind=0; ind<$panels.length; ++ind) {
        getShortestCol($columns).append($panels[ind]);
      }
      
      // Put gaps
      if ( options.createGaps ) {
        var maxH = getLongestCol($columns).height();

        for(var ind=0; ind<$columns.length; ++ind) {
          var $col = $columns[ind];
          var thisH = $col.height();
          var numEle = $col.children().length;
          // Create gaps
          if ( thisH!=maxH && numEle>1 ) {
            var gap = (maxH-thisH)/(numEle-1);
            
            $col.children().each(function(index){
              console.log(index + ' ' + this);
              if ( index<(numEle-1) ) {
                var $this = $(this);
                // @todo : hard coded, we suppose is in px
                $this.css('margin-bottom', (parseInt($this.css('margin-bottom')) + gap) + 'px');
              }
            });
          }
        }
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

    // ---------------------------------------------------------- Public Methods
   
    
    // --------------------------------------------------------- Private Methods
    function getOptions($el) {
      return $el.data('plugin_' + pluginName + '_option');
    }

    function setOptions($el, options) {
      return $el.data('plugin_' + pluginName + '_option', options);
    }
    
    function getShortestCol($columns) {
      var currInd=null;
      for(var ind=0; ind<$columns.length; ++ind) {
        if ( currInd==null || $columns[ind].height() < $columns[currInd].height() ) {
          currInd=ind;
        }
      }
      
      return $columns[currInd];
    }

    function getLongestCol($columns) {
      var currInd=null;
      for(var ind=0; ind<$columns.length; ++ind) {
        if ( currInd==null || $columns[ind].height() > $columns[currInd].height() ) {
          currInd=ind;
        }
      }
      
      return $columns[currInd];
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
