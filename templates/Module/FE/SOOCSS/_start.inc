<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{i18n(APP_WEB_TITLE)}</title>
  <!-- !CSS -->
  <link href="{urlSoocss(/css/soocss.min.css)}" rel="stylesheet">
  <link href="{urlSoocss(/css/style.css)}" rel="stylesheet">
  
  <link href="{urlSoocss(/css/jquery-ui.min.css)}" rel="stylesheet">
  <link href="{urlSoocss(/css/jquery-ui.structure.min.css)}" rel="stylesheet">
  <link href="{urlSoocss(/css/jquery-ui.theme.min.css)}" rel="stylesheet">
  
  <link rel="shortcut icon" href="favicon.ico" type="image/x-icon">
    <!-- HTML5 Shim and Respond.js IE8 support of HTML5 elements and media queries -->
  <!-- WARNING: Respond.js doesn't work if you view the page via file:// -->
  <!--[if lt IE 9]>
    <script src="{urlSoocss(/js/html5shiv.js)}"></script>
    <script src="{urlSoocss(//js/respond.min.js)}"></script>
    <script src="{urlSoocss(//js/selectivizr.js)}"></script>
  <![endif]-->

  <!-- !JavaScript -->
  <script src="{urlSoocss(/js/jquery.js)}"></script>
  <script src="{urlSoocss(/js/jquery-ui.min.js)}"></script>
  <script src="{urlSoocss(/js/bootstrap.js)}"></script>
  <script src="{urlSoocss(/js/soocss.js)}"></script>
  ## OK, I'm not very produ of that, but this is the problem:
  ## - To nake the things easier when deploying, wwe are using relative 
  ##   paths instead absoulte ones (crossfinger)
  ## - The file /js/scripts.js need to call BE's services
  ## - Depending on weather we're in a module's page (one inside 
  ##   [appContext]/fe/[module]/page) or a generic one ([appContext]/fe/login.html, ...) 
  ##   the path to the BE is one or another, so it MUST receive that context
  <script>
  var BE_CONTEXT = "{urlBE(/)}";
  </script>
  <script src="{urlSoocss(/js/scripts.js)}"></script>

  <!--
  ==================================================== 
  START : no SOOCSS code
  ==================================================== 
  -->
  <style>
  ._template {
    display:none !important;
  }
  .clicable:hover {     
    cursor: pointer;    
  }                     
  </style>
  <!-- My libraries (those should be replaced by Standard ones) -->
  <script src="{urlInternal(/js/jquery.jsonform.js)}"></script>
  <script src="{urlInternal(/js/jquery.ajaxlist.js)}"></script>
  <script src="{urlInternal(/js/jquery.jsonrender.js)}"></script>
  <script src="{urlFE(/utils.js)}" ></script>
  <script>
  // Once the page has been:
  // - Propery loaded
  // - Checked that the current userr has permissions to access this page
  // - Translated
  // this is the place to put some common code
  // @TODO : has sense? If we want to put some common code, why do not put it in
  // _end.ind that is where this event is thrown?
  $(document).on("custom.ready", function(e, widgetData) {
    // $('#goHome').attr('href', currUser['OnLoginUrl']);
    $('._goHome, #breadcrumb .ci-home').click(function() {       
      if ( widgetData && widgetData['User'] && widgetData['User']['OnLoginUrl'] ) {
        // widgetData['User']['OnLoginUrl']; has the form /[module]/....
        document.location = '..' + widgetData['User']['OnLoginUrl']; 
      } else {
        document.location = "{urlFE(/)}"; 
      }
    });
    /*var app = angular.module('myApp', ['pascalprecht.translate'])

    //var app = angular.module('myApp', []);
    app.config(function ($translateProvider) {
      $translateProvider.translations({
        TITLE: 'Hello',
        FOO: 'This is a paragraph.',
        BUTTON_LANG_EN: 'english',
        BUTTON_LANG_DE: 'german'
      });
    });
    
    app.run(function($rootScope) {
      $rootScope.name = "World";
    });*/
  });
  </script>
  <!-- Custom CSS -->
  <link href="{urlFE(/css/main.css)}" rel="stylesheet">
  <link href="{urlBE(/action/_ConfigApp/controller/GetCss)}" rel="stylesheet">
  <!--
  ==================================================== 
  END : no SOOCSS code
  ==================================================== 
  -->
</head>

<body id="{PageID}" class="{PageClassname}">
  <!-- !main content -->
  <div class="page-wrapper">
    <!-- !navbar -->
    <header class="header">
      <!-- !list-langs -->
      <div class="w-100 sub-head">
        <div class="container-fluid" id="submenu">
          <h2 class="mvs fsm _i18n">{i18n(SwitchLang)}</h2>
          <ul id="allLangs" class="list-inline">
            <li class="col-xs-4 col-sm-3 col-md-2 mbm _template">
              <button class="btn btn-default w-100">
                <span class="Locale _i18n"></span>
              </button>
            </li>
          </ul>
        </div>
      </div>
      <!-- /list-langs -->


      <div class="container-fluid">
        <div class="row">
          <!-- !the logo box -->
          <div class="col-xs-12 col-sm-6 pts">
            <span class="sr-only"></span>
            <img class="clicable _goHome  d-inline-block mrm mbs" src="{urlBE(/action/_ConfigApp/controller/GetLogo)}" width="50px" alt="logo" onError="this.src='{urlFE(/img/logo.png)}';" />
            <span class="_i18n fsl d-inline-block v-middle">{i18n(APP_WEB_NAME)}</span>
          </div>
          <!-- /the logo box -->

          <!-- !the menu box -->
          <div class="header-demo col-xs-12 col-sm-6">
            <ul class="list-inline pull-right">
              <li class="hidden-xs hidden-sm hidden-md hidden-lg">
                <select class="btn btn-default">
                  <option class="_i18n">{i18n(SelectLang)}</option>
                 </select>
              </li>
              <li>
                <a href="#" class="open-submenu">
                  <span class="submenu-item _i18n">{i18n(Languages)}</span>
                  <span class="ci ci-chevron-down fsl pls"></span>
                </a>
              </li>
              <!--
              <li>
                <a href="#">
                  <span class="submenu-item">Help</span>
                  <span class="ci ci-info fsl pls"></span>
                </a>
              </li>
              -->
              ## By default, hide the icon with the user
              <li id="_userIcon" style="display:none;">
                <a href="{urlFE(/_User/ViewMySelf_User.html)}">
                  <span id="_userName" class="submenu-item"></span>
                  <span class="ci ci-user fsl pls"></span>
                </a>
              </li>

              ## By default, hide the logout button
              <li id="_doLogout" style="display:none;">
                <a href="#">
                  <span class="submenu-item _i18n">{i18n(Logout)}</span>
                  <span class="ci ci-logout fsl pls"></span>
                </a>
              </li>
            </ul>
          </div>
          <!-- /the menu box -->

          <!-- !the action box -->
          <div class="header-actions">
          </div>
          <!-- /the action box -->
        </div>
      </div>      
    </header>
    <!-- /navbar -->

    <div class="container-fluid demos">
      <!-- Message OK : we have ONLY ONE, even for composed pages -->
      <div id="pMsgOK" style="display:none;" 
        class="alert alert-success alert-dismissable">
        <button type="button" class="close" data-dismiss="alert" aria-hidden="true">
          <span class="ci ci-close"></span>
        </button>
        <span class="ci ci-success"></span>
        <span class="fwb"></span>
      </div>

      ## This is the new breadcrumb      
      @@if {TestOutputBreadrumb}
      <!-- !breadcrumb -->
      <div id="breadcrumb" class="w-100">
        <div class=" d-table mtm">
          <span class="ci ci-home d-table-cell fsxxl v-middle prs clicable"></span>
          <ol class="list-inline fsl mtm d-table-cell v-middle">
            <!--
            <li class="phn">
              <a href="#">Candidatura: Partido de España 04</a>
              <span class="ci ci-chevron-right v-middle"></span>
            </li>
            -->
          </ol> 
        </div>
      </div>
      <!-- /breadcrumb -->
      @@endif