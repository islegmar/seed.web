/**
 * In an input test we introduce an address and it is validated agains google
 * 
 * A jQuery plugin boilerplate.
 * Author: Jonathan Nicol @f6design
 * http://f6design.com/journal/2012/05/06/a-jquery-plugin-boilerplate/
 */
;(function($) {
  // Change this to your plugin name.
  var pluginName = 'inputGoogleAddressAutocomplete';
  
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
      'isDebug'         : true,
      'selectorAddress' : '[name=address]',
      'selectorLat'     : '[name=lat]',
      'selectorLng'     : '[name=lng]'
    }, $.fn[pluginName].defaults, options);

    /**
     * Initialize plugin.
     */
    function init() {
      /*
      <div class="address" data-jsonform-group="address">
        <label>Introduce location</label>
        <input id="autocomplete"  type="text" name="content" onFocus="geolocate()" size="100"></input>
        <div class="map-canvas"></div>
        <input type="hidden" name="lat"/>
        <input type="hidden" name="lng"/>
      </div>
      */
    
    
      
      // -------------------------------------------------------Autocomplete address
      var autocomplete = new google.maps.places.Autocomplete (
        $el.find(options.selectorAddress).get(0),
        { 
          types: ['geocode'] 
        }
      );
      /*
      var $mapCanvas = $('.address .map-canvas');
      var map = new google.maps.Map($mapCanvas.get(0), {
        zoom: 8
      });
      */    
      // When the user selects an address from the dropdown,get the Lat/Lng
      google.maps.event.addListener(autocomplete, 'place_changed', function() {
        alert(this);
        var place = autocomplete.getPlace();
        var location = place.geometry.location;
        $el.find(options.selectorLat).val(location.lat());
        $el.find(options.selectorLng).val(location.lat());
        /*
        if (place.geometry) {
          map.panTo(place.geometry.location);
          map.setZoom(15);
        } 
        $mapCanvas.show();*/
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

    // ---------------------------------------------------------- Public Methods
   
    
    // --------------------------------------------------------- Private Methods
    function getOptions($el) {
      return $el.data('plugin_' + pluginName + '_option');
    }

    function setOptions($el, options) {
      return $el.data('plugin_' + pluginName + '_option', options);
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
