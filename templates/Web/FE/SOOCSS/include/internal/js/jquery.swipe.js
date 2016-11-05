/**
 * Swipe for mobile applications
 * Thanks to http://padilicious.com/code/touchevents/
 * 
 * TOUCH-EVENTS SINGLE-FINGER SWIPE-SENSING JAVASCRIPT
 * Courtesy of PADILICIOUS.COM and MACOSXAUTOMATION.COM
 * this script can be used with one or more page elements to perform actions based on them being swiped with a single finger
 *
 * A jQuery plugin boilerplate.
 * Author: Jonathan Nicol @f6design
 * http://f6design.com/journal/2012/05/06/a-jquery-plugin-boilerplate/
 */
;(function($) {
  // Change this to your plugin name.
  var pluginName = 'swipe';
  
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
    
    // Swipe vars
    var triggerElementID = null; // this variable is used to identity the triggering element
    var fingerCount = 0;
    var startX = 0;
    var startY = 0;
    var curX = 0;
    var curY = 0;
    var deltaX = 0;
    var deltaY = 0;
    var horzDiff = 0;
    var vertDiff = 0;
    var minLength = 72; // the shortest distance the user may swipe
    var swipeLength = 0;
    var swipeAngle = null;
    var swipeDirection = null;
    // NOTE: the touchStart handler should also receive the ID of the triggering element
    // make sure its ID is passed in the event call placed in the element declaration, like:
    // <div id="picture-frame" ontouchstart="touchStart(event,'picture-frame');"  ontouchend="touchEnd(event);" ontouchmove="touchMove(event);" ontouchcancel="touchCancel(event);">
    
    // Extend default options with those supplied by user.
    options = $.extend({
      fLog        : null,
      fSwipeRight : null,
      fSwipeLeft  : null,
      fSwipeUp    : null,
      fSwipeDown  : null
    }, $.fn[pluginName].defaults, options);

    /**
     * Initialize plugin.
     */
    function init() {
      el.addEventListener("touchstart" , touchStart , false);
      el.addEventListener("touchend"   , touchEnd   , false);
      el.addEventListener("touchmove"  , touchMove  , false);
      el.addEventListener("touchcancel", touchCancel, false);
      
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
    function touchStart(event) {
      if ( options.fLog ) options.fLog('touchStart');
      
      // disable the standard ability to select the touched object
      event.preventDefault();
      // get the total number of fingers touching the screen
      fingerCount = event.touches.length;
      if ( options.fLog ) options.fLog('touchStart> fingerCount : ' + fingerCount);
      // since we're looking for a swipe (single finger) and not a gesture (multiple fingers),
      // check that only one finger was used
      if ( fingerCount == 1 ) {
        // get the coordinates of the touch
        startX = event.touches[0].pageX;
        startY = event.touches[0].pageY;
        // store the triggering element ID
        //triggerElementID = passedName;
      } else {
        // more than one finger touched so cancel
        touchCancel(event);
      }
    }
  
    function touchMove(event) {
      if ( options.debug ) console.log('touchMove');
      
      event.preventDefault();
      if ( event.touches.length == 1 ) {
        curX = event.touches[0].pageX;
        curY = event.touches[0].pageY;
      } else {
        touchCancel(event);
      }
    }
    
    function touchEnd(event) {
      if ( options.debug ) console.log('touchEnd');

      event.preventDefault();
      // check to see if more than one finger was used and that there is an ending coordinate
      if ( fingerCount == 1 && curX != 0 ) {
        // use the Distance Formula to determine the length of the swipe
        swipeLength = Math.round(Math.sqrt(Math.pow(curX - startX,2) + Math.pow(curY - startY,2)));
        // if the user swiped more than the minimum length, perform the appropriate action
        if ( swipeLength >= minLength ) {
          caluculateAngle();
          determineSwipeDirection();
          processingRoutine();
          touchCancel(event); // reset the variables
        } else {
          touchCancel(event);
        } 
      } else {
        touchCancel(event);
      }
    }
  
    function touchCancel(event) {
      // reset the variables back to default values
      fingerCount = 0;
      startX = 0;
      startY = 0;
      curX = 0;
      curY = 0;
      deltaX = 0;
      deltaY = 0;
      horzDiff = 0;
      vertDiff = 0;
      swipeLength = 0;
      swipeAngle = null;
      swipeDirection = null;
      triggerElementID = null;
    }
    
    function caluculateAngle() {
      var X = startX-curX;
      var Y = curY-startY;
      var Z = Math.round(Math.sqrt(Math.pow(X,2)+Math.pow(Y,2))); //the distance - rounded - in pixels
      var r = Math.atan2(Y,X); //angle in radians (Cartesian system)
      swipeAngle = Math.round(r*180/Math.PI); //angle in degrees
      if ( swipeAngle < 0 ) { swipeAngle =  360 - Math.abs(swipeAngle); }
    }
    
    function determineSwipeDirection() {
      if ( (swipeAngle <= 45) && (swipeAngle >= 0) ) {
        swipeDirection = 'left';
      } else if ( (swipeAngle <= 360) && (swipeAngle >= 315) ) {
        swipeDirection = 'left';
      } else if ( (swipeAngle >= 135) && (swipeAngle <= 225) ) {
        swipeDirection = 'right';
      } else if ( (swipeAngle > 45) && (swipeAngle < 135) ) {
        swipeDirection = 'down';
      } else {
        swipeDirection = 'up';
      }
    }
    
    function processingRoutine() {
      var swipedElement = el;// document.getElementById(triggerElementID);
      if ( swipeDirection == 'left' && options.fSwipeLeft ) {
        options.fSwipeLeft($el);
      } 
      
      if ( swipeDirection == 'right' && options.fSwipeRight ) {
        options.fSwipeRight($el);
      } 
      
      if ( swipeDirection == 'up' && options.fSwipeUp ) {
        options.fSwipeUp($el);
      } 
      
      if ( swipeDirection == 'down' && options.fSwipeDown ) {
        options.fSwipeDown($el);
      } 
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
