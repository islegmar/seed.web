/**
 * Tenemos un tabbed menú del tipo
 * 
 * <div>
 *  <div class="header">
 *    header1
 *    header2
 *    ...
 *  </div>
 *  <div class="content">
 *    content1
 *    content2
 *    ...
 *  </div>
 * </div>
 * 
 * de manera que:
 * - Todos los headerN son visible pero sólo hay uno seleccionado
 * - Sólo un contentN es visible cada vez
 * - Al hacer click en headerX el correspondiente contnetX se visible
 *
 * IL - 06/02/14 - Make this plugins clonable
 * We have added 'selector2OriginalElementFromClikedHeader' as a 'patch' to make 
 * this plugin 'clonable'. 
 *   
 * A jQuery plugin boilerplate.
 * Author: Jonathan Nicol @f6design
 * http://f6design.com/journal/2012/05/06/a-jquery-plugin-boilerplate/
 */
;(function($) {
  // Change this to your plugin name.
  var pluginName = 'tabbedMenu';
  
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
    var currInd = 0;
    
    // Extend default options with those supplied by user.
    options = $.extend({
      'isDebug'         : false,
      'selectorHeader'  : '> .header',
      'selectorContent' : '> .content',
      'classActive'     : 'active',
      'onSelected'      : null,
      /* If true, the user can not click for change the tab (it is done by code, 
       * useful for wizards)
       */
      'blockTabs'       : false,
      /**
       * If set, it is the selector that allows how to find $el from the clicked 
       * element in the header. If not set, variable $el is used.
       * This is useful when this tabbedMenu is set in cloned elements
       */
      'selector2OriginalElementFromClikedHeader' : null,
      'autoSelectInd' : 0,
      /* IL - 31/01/15 - If set, that means this select the components that 
      form the set with the header's items and content's items. If not, then
      it is used that are the children() of selectorHeader and selectorContent.
      In fact, the original behaviour can obtained with > * == children() */
      'selectorHeaderItems' : null,
      'selectorContentItems' : null
    }, $.fn[pluginName].defaults, options);

    /**
     * Initialize plugin.
     */
    function init() {
      if ( options.isDebug ) console.log('tabbedMenu.init> el : ' + $el.attr('class') + ', selectorContent : ' + options.selectorContent);
      if ( !options.blockTabs ) {
        // Add a listener, so when click on a certain 'tab' the corresponding
        // panel is set as active. This listener is ok when cloned
        var $listHeaderItems = null;

        // IL - 31/01/15
        if ( options.selectorHeaderItems ) {
          // It is not 100% needed, but try to avoid mixing of selecting methods
          if ( ! options.selectorContentItems ) {
            throw 'You must set both selectorHeaderItems and selectorContentItems';
          }
          $listHeaderItems = $el.find(options.selectorHeaderItems);
        } else {
          $listHeaderItems = $el.find(options.selectorHeader).children();
        }

        // When click on an item header, select the corresponding content 
        $listHeaderItems.click(function(e){
          var $this = $(this);
          if ( options.isDebug ) {
            console.log('Click on tab ' + $this.index());
          }
  
          if ( options.selector2OriginalElementFromClikedHeader ) {
            console.log('>>>>> ' + $this.closest( options.selector2OriginalElementFromClikedHeader).attr('class'));
            selectOption($this.index(), $this.closest( options.selector2OriginalElementFromClikedHeader));
          } else {
            selectOption($this.index());
          }
        })
      }
      // Select the first option
      if ( options.autoSelectInd!=null ) {
        selectOption(options.autoSelectInd);
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
    /* Go to the next tab */
    function next() {
      return selectOption(currInd+1);
    }

    /* Go to the previous tab */
    function prev() {
      return selectOption(currInd-1);
    }
    
    /**
     * We have selected one of the opctions
     */
    function selectOption(index, $pOriginalEl) {
      var $originalEl = $pOriginalEl ? $pOriginalEl : $el;
      
     var $listHeaderItems = null;
      var $listContentItems = null;
      if ( options.selectorContentItems ) {
        $listHeaderItems = $originalEl.find(options.selectorHeaderItems);
        $listContentItems = $originalEl.find(options.selectorContentItems);
      } else {
        $listHeaderItems = $originalEl.find(options.selectorHeader).children();
        $listContentItems = $originalEl.find(options.selectorContent).children();
      }

      if ( options.isDebug ) {
        console.log('selectOption (index:' + index + 
          ', $pOriginalEl:' + ($pOriginalEl ? 'value set' : 'value not set') + 
          ', $originalEl: ' + $originalEl.attr('class') + ')');
        console.log('selectorHeaderItems : ' + options.selectorHeaderItems + 
          ', selectorHeader : ' + options.selectorHeader +
          ', # $listHeaderItems : ' + $listHeaderItems.length);
        console.log('selectorContentItems : ' + options.selectorContentItems + 
          ', selectorContent : ' + options.selectorContent +
          ', # $listContentItems : ' + $listContentItems.length);
      }

 
      // Remove the active header/content
      $listHeaderItems.removeClass(options.classActive);
      $listContentItems.removeClass(options.classActive);
      
      // Set this active/content
      $listHeaderItems.eq(index).addClass(options.classActive);
      $listContentItems.eq(index).addClass(options.classActive);

      if ( options.onSelected ) {
        options.onSelected(index, $originalEl);
      }
      currInd = index;
      
      return currInd;
    }
    
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
      destroy: destroy,
      next : next,
      prev : prev,
      selectOption : selectOption
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
