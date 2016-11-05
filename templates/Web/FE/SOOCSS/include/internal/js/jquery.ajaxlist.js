/**
 * Build a list using AJAX
 * 
 * A jQuery plugin boilerplate.
 * Author: Jonathan Nicol @f6design
 * http://f6design.com/journal/2012/05/06/a-jquery-plugin-boilerplate/
 */
;(function($) {
  // Change this to your plugin name.
  var pluginName = 'ajaxlist';
 
  /**
   * Plugin object constructor.
   * Implements the Revealing Module Pattern.
   */
  function Plugin(element, options) {
    // References to DOM and jQuery versions of element.
    var el = element;
    var $el = $(element);
    // Nav buttons
    var $bNext;
    var $bPrev;
 
    // Extend default options with those supplied by user.
    options = $.extend({
      'url'                  : null,
      'extraUrlParams'       : null,
      'totPerPage'           : 10,
      'paramIndPage'         : 'indPage',
      'paramTotPerPage'      : 'totPerPage',
      'selIndPag'            : '.indPag',
      'selTotPag'            : '.totPag',
      'selTotRecords'        : '.totRecords',
      'selLoading'           : '.loading',
      'selNoData'            : '.empty',
      'selData'              : '.listado',
      'selContent'           : '.listado .content',
      'selButtonNext'        : '.bNext',
      'selButtonPrev'        : '.bPrev',
      'onRowCreated'         : null,
      'onListCreated'        : null,
      'addData2Row'          : true,
      /* IL - 30/10/13 - Set a class when an item list is clicked */
      'classOnListItemClicked' : 'active'
    }, $.fn[pluginName].defaults, options);
    
    /**
     * Initialize plugin.
     */
    function init() {
      // Prev button 
      $bPrev = $el.find(options.selButtonPrev);
      $bPrev.click(function(){
        var data = $el.data('plugin_' + pluginName + '_data');
        getList(data.indPage-1, data.totPerPage);
      });
      
      // Next button 
      $bNext = $el.find(options.selButtonNext);
      $bNext.click(function(){
        var data = $el.data('plugin_' + pluginName + '_data');
        getList(data.indPage+1, data.totPerPage);
      });
      getList(0, options.totPerPage);
      
      if ( options.classOnListItemClicked ) {
        $el.find('._template').click(function(){
          var $this = $(this);
          $this.parent().children().removeClass(options.classOnListItemClicked);
          $this.addClass(options.classOnListItemClicked);
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
        $el.removeData('plugin_' + pluginName + '_data');
        
        
        hook('onDestroy');
        // Remove Plugin instance from the element.
        $el.removeData('plugin_' + pluginName);
      });
    }
    
    // --------------------------------------------------------- Private Methods

    // --------------------------------------------------------- Public Methods
    /**
     * Build the list for a certain page
     */
    function getList(indPage, totPerPage) {
      // Hide all panels but Loading...
      if ( options.selLoading ) $el.find(options.selLoading).show();
      if ( options.selData )    $el.find(options.selData).hide();
      if ( options.selNoData )  $el.find(options.selNoData).hide();
      
      //alert(options.paramIndPage + ',' + options.paramTotPerPage);
      urlParams = {};
      urlParams['indPage']    = indPage;
      urlParams['totPerPage'] = totPerPage;
      if ( options.extraUrlParams!=null ) {
        urlParams = $.extend(urlParams, options.extraUrlParams);
      }
      $.getJSON(
        options.url,
        urlParams,
        function(data) {
          if ( data.totPages==0 ) {
            var $content = $el.find(options.selContent);
            renderData($content,null);
            
            // Hide all panels but Empty...
            if ( options.selLoading ) $el.find(options.selLoading).hide();
            if ( options.selData )    $el.find(options.selData).hide(); 
            if ( options.selNoData )  $el.find(options.selNoData).show();
          } else {
            // Hide all panels but Data...
            if ( options.selLoading ) $el.find(options.selLoading).hide();
            if ( options.selData )    $el.find(options.selData).show(); 
            if ( options.selNoData )  $el.find(options.selNoData).hide();

            // Put the data
            var $content = $el.find(options.selContent);
            renderData($content,null);
            renderData($content,data.data, function($row, rowData, ind) {
              if ( options.addData2Row ) {
                // console.log('Add data ' + 'plugin_' + pluginName + '_data into ' + $row.attr('class'));
                $row.data('plugin_' + pluginName + '_data', rowData);
              }
            
              if ( options.onRowCreated ) {
                options.onRowCreated($row, rowData, ind);
              }
            }, options.onListCreated);  

            /* Info */ 
            $el.find(options.selIndPag).html(data.indPage+1);
            $el.find(options.selTotPag).html(data.totPages);
            $el.find(options.selTotRecords).html(data.totRecords);
            
            /* Now, show/hide the prev/next buttons */
            // First page : hide previous button
            if ( data.indPage==0 ) {
              $bPrev.attr('disabled','disabled');
            } else {
              $bPrev.removeAttr('disabled');
            }
      
            // Last page : hide next button
            if ( data.indPage==(data.totPages-1) ) {
              $bNext.attr('disabled','disabled');
            } else {
              $bNext.removeAttr('disabled');
            }
            
            /* Set some data for the nav buttons (see below) */
            $el.data('plugin_' + pluginName + '_data', data);
          }
        }
      ).error(function(){
        //alert('Error on ' + options.url);
        console.log('Error on ' + options.url);
      }); 
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
      getList : getList
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
