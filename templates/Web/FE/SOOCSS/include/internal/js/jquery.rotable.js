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
  var pluginName = 'rotable';
  
  /**
   * Plugin object constructor.
   * Implements the Revealing Module Pattern.
   */
  function Plugin(element, options) {
    
    // References to DOM and jQuery versions of element.
    var el = element;
    var $el = $(element);
    
    // Extend default options with those supplied by user.
    options = $.extend({
    }, $.fn[pluginName].defaults, options);

    /**
     * Initialize plugin.
     */
    function init() {
      //Add a button that torate CW (clockwise)
      var $bRotateCW=$('<button type="button" class="bRotateCW"/>');
      $bRotateCW.click(function() {
        rotateRight();
      });
      $el.append($bRotateCW);
      
      //Add a button that torate CCW (counter-clockwise)
      var $bRotateCCW=$('<button type="button" class="bRotateCCW"/>');
      $bRotateCCW.click(function() {
        rotateLeft();
      });
      $el.append($bRotateCCW);
      
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
    /**
     * Rotate to the rigth inc degrees. If not defined, the default value is used.
     */
    function rotateRight(inc) {
      incAngle(!inc ? 15 : inc);
    }
    
    /**
     * Rotate to the left inc degrees. If not defined, the default value is used.
     */
    function rotateLeft(inc) {
      incAngle(!inc ? -15 : -inc);
    }

    /**
     * Incremente the angle (it can be + or -)
     */
    function incAngle(incAngle) {
      // Find the actual angle for that element
      var actualAngle = $el.data(pluginName + "_angle");
      // If not defined, let's suppose 0
      if ( !actualAngle ) actualAngle  = 0;
      
      // Calculate the new angle and store it
      var newAngle = actualAngle  + incAngle;
      $el.data(pluginName + "_angle", newAngle);

      console.log("Rotate. actualAngle : " + actualAngle + 
          ", newAngle : " + newAngle);
      
      // Let's rotate!
      $el
        .css('-webkit-transform', 'rotate(' + newAngle + 'deg)')
        .css('-o-transform', 'rotate(' + newAngle + 'deg)') 
        .css('transform', 'rotate(' + newAngle + 'deg)');
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
