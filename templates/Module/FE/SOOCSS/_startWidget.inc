<!--
## HTML for EACH widget
## @TODO : probably we can add more content here, if we define a common widget
## structure, as 
## - Title
## - Description
## - OK message
## - ERROR message
## - Actions
-->
<!-- WHOAMI : {MODULE}:{ActionName} -->
<!-- !widgetPanel -->
<div id="{NewWidgetID}" class="widgetPanel {MODULE}_{ActionName}">
  <!--
  @TODO : a big one! We do NOT put this code here because a widget can contain 
  other widgets and we can have problems with the IDs
  -->
  <script>
  ## At this point widgetData contains: 
  ## + All the request parameters
  ## + 'User' = { ... logged user ... } 
  ## so this this data is COMMON for all the widgets we are are rendering 
  ## (usually on or more that one in case of composed pages)
  ##
  ## @TODO : VERY CAREFUL, widgetData is passed by reference
  ## The code I had before was:
  ##
  ##   $(document).on('custom.ready', function(evt, widgetData){
  ##     (1) Here we have received a widgetData, the same for ALL the widgets
  ##     ...
  ##     widgetData['actionParams'] = ..... => (2) Change widgetData
  ##     ...
  ##     $('#<WidgetID>').trigger("custom.widgetReady", widgetData); ==> Rethrow the data
  ##   });  
  ## 
  ##   $('#<WidgetID>').on("custom.widgetReady", function(evt, widgetData){
  ##     (3) Each widget receive a DIFFERENT widgetData
  ##     var $container = $('#frm{CurrentWidgetID}');
  ##     $.getJSON( ==> Asynch action
  ##       function(data) {
  ##         (4) We want to use widgtData
  ##       }
  ##     );
  ##   });
  ##
  ## The problem is that widget data in (3) and (4) are differents.
  ## In (3) was ok but in (4) it looks like it was changed by another widget
  ## 
  ## So the solution is (I do not know it there is a better one) to clone 
  ## widgetData
  $(document).on('custom.ready', function(evt, pWidgetData){
    // Clone it, see comment above
    var widgetData=$.extend({},pWidgetData);
    var usr = widgetData['User'];

    /* 
    Once the page is loaded, every widget will receive an event and then 
    will check if this widget has the permissions. If it has, then the widget
    can be rendered
    */
    // User has permission
    if ( !'{PermissionName}'.trim() || usr['permissions'].indexOf('{PermissionName}'.trim()) > -1 ) { 
      // console.log('[{CurrentWidgetID}] User has the required permission {PermissionName}');
      $('#{CurrentWidgetID} ._widgetContent').show();
      $('#{CurrentWidgetID} ._noPermission').hide();

      // OK, now add in the widgetData the SPECIFIC data for that widget, taking
      // into acount the params this widget receives, taking as source of values
      // the actual widgetData. This part is very IMPORTANT because this define
      // the local scope of the variables; that is EVERYTHING inside this widget
      // that uses variables, will use the values from widgetData['actionParams']
      // Some samples:
      // + The Load action
      widgetData['actionParams'] = {ActionParamsObject(widgetData)};

      // console.log('>>>>> {MODULE}:{ActionName}. widgetData : ' + JSON.stringify(widgetData));

      // Trigger an event to the widget, so it can continue working
      $('#{CurrentWidgetID}').trigger("custom.widgetReady", widgetData);
    // No permission
    } else {
      /*console.log('[{CurrentWidgetID}] User has NOT the required permission {PermissionName}');
      $('#{CurrentWidgetID} ._noPermission').show();
      $('#{CurrentWidgetID} ._widgetContent').hide();*/
      document.location='{urlFE(/)}';
    }
  });
  </script>

  <div class="_noPermission _i18n" style="display:none;">{i18n(NoPermission)}</div>
  <!-- !widgetContent -->
  <div class="_widgetContent {CollapsedClass}"><!-- Message ERROR -->
    <!-- ALL widgets have a panel errors -->
    <div id="p{CurrentWidgetID}Errors" style="display:none;"  
      class="alert alert-danger">
      <span class="ci ci-error"></span>
      <span class="fwb"></span>
    </div>