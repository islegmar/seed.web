/**
 * Canvas for painting.
 * 
 * $el is the reference to the canvas
 * 
 * CHANGES
 * 23/07/13   V2 - Use PaperJS for drawing
 *            In order to use this plugin, you should include paper
 *            <script type="text/javascript" src="/external/paperJS/V0.9.8/dist/paper.js"></script>
 *            
 * A jQuery plugin boilerplate.
 * Author: Jonathan Nicol @f6design
 * http://f6design.com/journal/2012/05/06/a-jquery-plugin-boilerplate/
 */
;(function($) {
  // Change this to your plugin name.
  var pluginName = 'canvaspainter';
 
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
      /* Where we find the different panels */
      "classPColores"  : "pColores",
      "classPBorrar"   : "pBorrar",
      "classPLienzo"   : "pLienzo",
      "classPGrosores" : "pGrosores",
      "classPComandos" : "pComandos",
      "colors"         : [ 'black', "#cb3594", "#659b41", "#ffcf33", "#986928"],
      "grosores"        : [
        { name : 'grosorExtraFino'  , value : 1},
        { name : 'grosorFino'       , value : 1},
        { name : 'grosorNormal'     , value : 4},
        { name : 'grosorGrueso'     , value : 8},
        { name : 'grosorExtraGrueso', value : 15}
      ],
      /* If defined, when putting and getting images we scale */
      "scaleFactor" : null
    }, $.fn[pluginName].defaults, options);
    
    // The canvas where we are going to draw
    var canvas = null;
    var context = null;
    var testX = 0;
    var testY = 0;
    // The path that we're going to draw
    var paperPath = null;
    
    /**
     * Initialize plugin.
     */
    
    function init() {
      // Info about painting
      var isPainting = false;
      var lastPoint = null;
      var strokeStyle = 'black';
      var lineWidth = 5;
      
      // The panels
      var $pColores  = $el.find("." + options.classPColores);
      var $pBorrar   = $el.find("." + options.classPBorrar);
      var $pLienzo   = $el.find("." + options.classPLienzo);
      var $pGrosores = $el.find("." + options.classPGrosores);
      var $pComandos = $el.find("." + options.classPComandos);
      
      // Put the colors
      if ( options.colors ) {
        var $selectedColor = null;
        
        for (var ind=0; ind<options.colors.length; ++ind) {
          var color = options.colors[ind];
          
          // Create a color selector
          var $colorSelector = $('<span></span>');
          $colorSelector.css('background-color', color);
          
          // Add it to the panel
          $pColores.append($colorSelector);
          
          
          // Select this colot when click
          $colorSelector.bind('click', {color : color}, function(evt){
            var data = evt.data;
            var color = data.color;

            //console.log('color ' + color  + ' selected');
            // Mark this color as selected
            if ( $selectedColor !=null ) $selectedColor.removeClass('_selected');
            $selectedColor = $(this);
            $selectedColor.addClass('_selected');
            strokeStyle = color;
          });

          // Select the first
          if ( $selectedColor==null )  {
            $colorSelector.trigger('click');
          }
        }
      }
      
      // Put the grosores
      if ( options.grosores) {
        var $selectedGrosor = null;
        
        for (var ind=0; ind<options.grosores.length; ++ind) {
          var grosor = options.grosores[ind];
          
          // Create a grosor selector
          var $grosorSelector = $('<span class="' + grosor.name + '"></span>');
          
          // Add it to the panel
          $pGrosores.append($grosorSelector);
          
          
          // Select this colot when click
          $grosorSelector.bind('click', {grosor : grosor}, function(evt){
            var data = evt.data;
            var grosor = data.grosor;

            //console.log('grosor ' + grosor + ' selected');
            // Mark this color as selected
            if ( $selectedGrosor!=null ) $selectedGrosor.removeClass('_selected');
            $selectedGrosor = $(this);
            $selectedGrosor.addClass('_selected');
            lineWidth = options.scaleFactor ? options.scaleFactor * grosor.value : grosor.value;
          });

          // Select the first
          if ( $selectedGrosor==null )  {
            $grosorSelector.trigger('click');
          }
        }
      }
      
      // Get the canvas and the context
      canvas = document.createElement('canvas');
      context = canvas.getContext("2d");
      var $canvas = $(canvas);
      $pLienzo.append($canvas);
      //canvas.width = newW;
      //$lienzo = $el.find("canvas");
      //lienzo = $lienzo.get(0);
      
      // Create an empty project and a view for the canvas:
      paper.setup(canvas);

      
      // Trace the mouse movements
      var mouseDraw = new MouseDraw();
      mouseDraw.setLienzo($pLienzo);
      mouseDraw.setUseParentOffset(false);
      mouseDraw.render();
      
      // Start Paint
      $pLienzo.bind('startPaint', function(evt, punto) {
        // Create a new path and set its stroke color to black:
        paperPath = new paper.Path({
          segments: [punto],
          strokeColor: strokeStyle,
          strokeWidth : lineWidth,
          strokeCap : 'round',
          strokeJoin : 'round',
          fullySelected: false
        });
        isPainting=true;
      });
      
      $pLienzo.bind('painting', function(evt, punto) {
        if ( isPainting ) {
          paperPath.add(punto);
        } 
      });
      $pLienzo.bind('endPaint', function(evt, punto) {
        paperPath.simplify(10);
        isPainting = false;
        lastPoint  = punto;
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
    
    // ---------------------------------------------------------- Public Methods
    /**
     * Put the image. 
     * @todo : should we scale also the thikness?
     */
    function putImage(image) {
      var w = image.width  * (!options.scaleFactor ? 1 : options.scaleFactor);
      var h = image.height * (!options.scaleFactor ? 1 : options.scaleFactor);
      
      console.log('putImage> w : ' + w + ', h : ' + h + '.');
      
      canvas.width = w;
      canvas.height = h;
      context.drawImage(image,0,0, w, h);
      
      // Draw a line (testing)
      /*
      context.strokeStyle = 'red';
      context.lineWidth = 10;
      context.beginPath();
      context.moveTo(w, 0);
      for(var ind=0; ind<=100; ++ind) {
        context.lineTo(w-ind*w/100, ind*h/100);
        context.stroke();
        console.log("ind : " + ind);  
      }
      */
    }
    
    /**
     * Get the actual contents as image
     * 
     * @returns
     */
    function getImage() {
      if ( options.scaleFactor ) {
        // Build a tmp canvas
        var tmpCanvas = document.createElement('canvas');
        var tmpContext = tmpCanvas.getContext("2d");
        
        // Set the good dimensions
        var newW = canvas.width  / options.scaleFactor;
        var newH = canvas.height / options.scaleFactor;
        tmpCanvas.width = newW;
        tmpCanvas.height = newH;
        
        // Draw (scale) on it
        tmpContext.drawImage(canvas,0,0, newW, newH);
        
        return tmpCanvas.toDataURL();
      } else {
        return canvas.toDataURL();
      }
    }
    
    function clear() {
      canvas.width = canvas.width;
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
      putImage : putImage,
      getImage : getImage,
      clear : clear
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
