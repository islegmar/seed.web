    </div><!-- /container -->

  </div><!-- /page-wrapper -->
  <!-- /main content -->

  <!-- !footer -->
    <footer class="page-footer">
    <div class="container">
      <div class="row">
        <div class="col-md-6 footer-left">
          &copy;Issi4u - <a href="http://www.issi4u.com">www.iss4u.com</a>
        </div>
        <div class="col-md-6 footer-right hidden-xs hidden-sm">
          Powered by <a href="https://github.com/islegmar/seed.web">seed.web</a>
        </div>
      </div>
    </div>
  </footer>

  <!--
  Reusable modal popup. This is shown every time is clicked an action configured
  with askConfirmation=true
  -->
  <div id="pAskConfirmation" class="modal fade" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <button id="btn_close_1" type="button" class="close" data-dismiss="modal" aria-hidden="true" title="Close">×</button>
          <h4 class="modal-title _i18n"></h4>
        </div>
        <div class="_i18n modal-body">
        </div>
        <div class="modal-footer">
          <button type="button" class="_btnNo btn btn-default _i18n" data-dismiss="modal">{i18n(AskConfirmationNo)}</button>
          <button type="button" class="_btnYes btn btn-primary _i18n">{i18n(AskConfirmationYes)}</button>
        </div>
      </div>
    </div>
  </div>

  <!--
  Hide resusable component for downloading files via Ajax
  -->
  <a id="downloadLink" href="" style="display: none;"></a>

  <!--
  ==================================================== 
  START : no SOOCSS code
  ==================================================== 
  -->
  <script>
  // ----------------------------------------------------------------- Init Load
  // When loading the page, we have to get a bunch of information from the server:
  // + The I18N
  // + The connected user 
  // + Any other information can appear in the future
  // In order to minimize the number of calls to the server, we request all this
  // info in a SINGLE call.
  // Because we can have pages composed by several widgets, any of them with 
  // its security retrictions, now the FIRST thing is to retrieve the I18N
  getPageInfo(
    {
    },
    function(user){
      // Show a success message in this page (if any). For example, this is the situation
      // if we return to a list after creating successfully an element
      displayMsgOK($('#pMsgOK'));

      // There is a user connected (
      // CAREFUL : we always receive an object user, but sometimes this is empty, so
      // we check the attribute Id to know if we really have an user connected or not
      if ( user && 'Id' in user ) {
        // ---- User Info
        // Show the icon 
        $('#_userIcon').show();

        // Show the user's name
        $('#_userName').html(user['Login']);

        // ---- Logout button
        // Show the logout button
        $('#_doLogout').show();

        // Logout when clicking (ask for confirmation)
        // @TODO : Add a link in the span instead this
        $('#_doLogout a').click(function(event){
          event.preventDefault();

          var i18nLogoutTitle="{i18n(_User:Logout:Title)}".translate();
          var i18nLogoutText="{i18n(_User:Logout:Text)}".translate();
          var logoutAction = {
            'beOnly' : true,
            'url' : '{urlBE(/service/Logout)}',
            'goOnActionDone' : '{urlFE(/)}'
          };

          askConfirmation(i18nLogoutTitle, i18nLogoutText, logoutAction);
          /*
          $.getJSON(
            '{urlBE(/service/Logout)}', 
            function(data) {
              document.location = '{urlFE(/)}';
            } 
          );
          */
        });

        $('body').addClass('role-' + user['role']);
      } else {
        $('body').addClass('role-anoymous');        
      }


      // Build the widgetdata that is composed by:
      // + The params in the url
      // + All the info coming from the user
      var widgetData = getUrlParams();
      widgetData['User'] = user;
      $(document).trigger( "custom.ready", widgetData);
    }
  ); // getPageInfo

  // -------------------------------------------------------------------- Logout
  
  // Collapsable panels
  $('.collapsable .page-title h1').click(function() {
    $(this).closest('.collapsable').toggleClass('expanded');
  });

  var tp = new TabbedPanel(); 
  tp.recoverLastClick();
  tp.rememberTheClicks();
  </script>
  <!--
  ==================================================== 
  END : no SOOCSS code
  ==================================================== 
  -->
</body>
</html>
