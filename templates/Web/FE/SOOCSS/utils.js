/**
 * Several JS utilities. 
 * This file MUST be in the root of /fe and it MUST receive the value of the 
 * variable BE_CONTEXT that is the context to access to the BE services.
 * Depending on weather this JS is used by a module's page or by a generic
 * one, the value is different, because to make the deployment easier we are
 * using relative paths instead absolute ones. 
 */

// Equivalent to $_GET
// Return an array with all the params
function getUrlParams() {
  var params = {};

  if (location.search) {
    var parts = location.search.substring(1).split('&');

    for (var i = 0; i < parts.length; i++) {
        var nv = parts[i].split('=');
        if (!nv[0]) continue;
        // params[nv[0]] = decodeURIComponent(nv[1]) || true;
        params[nv[0]] = decodeURIComponent(nv[1]);
    }
  }

  return params;
}

/**
 * Returns the value for a certain paramName for the current requeest
 */ 
// Global value to cache 
var __THIS_REQUEST_PARAMS__ = null; 
function getRequestValue(paramName) {
  if (__THIS_REQUEST_PARAMS__ ==null ) {
    __THIS_REQUEST_PARAMS__  = getUrlParams();
  }

  return paramName in __THIS_REQUEST_PARAMS__ ? __THIS_REQUEST_PARAMS__[paramName] : null;
}

// ----------------------------------------------------------------------- Utils
/**
 * Other utilities
 */

/**
 * http://stackoverflow.com/a/10997390/11236
 * Update a URL parameters (see http://stackoverflow.com/questions/1090948/change-url-parameters)
 * @TODO : does not take into account anchors!!
 */
function updateURLParameter(url, param, paramVal){
    var newAdditionalURL = "";
    var tempArray = url.split("?");
    var baseURL = tempArray[0];
    var additionalURL = tempArray[1];
    var temp = "";
    if (additionalURL) {
        tempArray = additionalURL.split("&");
        for (i=0; i<tempArray.length; i++){
            if(tempArray[i].split('=')[0] != param){
                newAdditionalURL += temp + tempArray[i];
                temp = "&";
            }
        }
    }

    var rows_txt = temp + "" + param + "=" + paramVal;
    return baseURL + "?" + newAdditionalURL + rows_txt;
}

/**
 * Add to a list of elements the current url params
 */
function addUrlParameters($listElements) {
  var urlParams = getUrlParams();
  $listElements.each(function(ind) {
    var $this = $(this);

    // It is an 'a'
    if ( $this.is('a')) {
      var url = $this.attr('href');
      for(var key in urlParams ) {
        url = updateURLParameter(url, key, urlParams[key]);
      }     
      $this.attr('href', url);
    } else {
      alert("Unknown data elemet type " + this);
    }

  });
}

/**
 * Return a new object with all the properties of obj1+obj2. 
 * If overwriteIfKeyExists==true, add also if the  property already exists in obj1.
 */
function extendObject(obj1, obj2, overwriteIfKeyExists) {
  var newObj={};

  // Obj1
  for(var key in obj1 ) {
    newObj[key]=obj1[key];
  }

  // Obj2
  for(var key in obj2 ) {
    if ( overwriteIfKeyExists || !newObj.hasOwnProperty(key) ) {
      newObj[key]=obj2[key];
    }
  }

  return newObj;
}

/** 
 * @TODO : Until we use SeedsFE or angular, this is just an utility to show the
 * form error messages and it uses a certain naming convention.
 */
function displayFormErrorMessages(errors, $pErrors) {
  $pErrors.show();
  var allErrors = "";
  for (var key in errors ) {
    // errors[key] can be one string (if we have one single error for that key)
    // or an array of strings (in case there are several errors)
    
    // List of errors
    if( $.isArray(errors[key]) ) {
      for(var ind=0; ind<errors[key].length; ++ind) {
        allErrors += errors[key][ind].translate() + ". "; 
      }
    // Single error  
    } else {
      allErrors += errors[key].translate() + ". "; 
    }
  }
  $pErrors.find('.fwb').html(allErrors);
}

function displayFormErrorMessagesSeparated(errors, $pErrors) {
  $pErrors.show();
  var allErrors = "";
  for (var key in errors ) {
    // errors[key] can be one string (if we have one single error for that key)
    // or an array of strings (in case there are several errors)
    
    // List of errors
    if( $.isArray(errors[key]) ) {
      for(var ind=0; ind<errors[key].length; ++ind) {
        allErrors += '<p>' + errors[key][ind].translate() + "</p>"; 
      }
    // Single error  
    } else {
      allErrors += '<p>' + errors[key].translate() + "</p>"; 
    }
  }
  $pErrors.find('.fwb').html(allErrors);
}

function hideFormErrorMessages($pErrors) {
  $pErrors.find('.fwb').html('');
  $pErrors.hide();
}

/** 
 * @TODO : Until we use SeedsFE or angular, this is just an utility to show the
 * success message after a form operation.
 */
function displayMsgOK($pMsgOK) {
  var msgCode = getItem('msgOK');
  if ( msgCode ) {
    $pMsgOK.show();
    $pMsgOK.find('.fwb').html(msgCode.translate());
    removeItem('msgOK');
    /*
    setTimeout(function(){
      $pMsgOK.fadeOut('slow')
    }, 2000);
    */
  }
}

function storeMsgOK(msg) {
  setItem('msgOK', msg);
}

/**
 * =============================================================================
 * @TODO : TEMPORAL SOLUTION (until we use angular)
 * =============================================================================
 */ 
// Global variable with all the translations
var TRANSLATIONS = {};
var ALL_LANGS = null;
var CURR_LANG = null;

/**
 * Add translate method to String.
 */ 
String.prototype.translate = function(params) {
  if ( !params ) params = getUrlParams()

  if ( this in TRANSLATIONS ) {
    found = TRANSLATIONS[this];
    // To improve the speed, check if the string contains variables, identified with $
    if ( found.indexOf("$")!=-1 ) {
      for (var paramName in params ) {
        var paramValue = params[paramName];
        found = found.replace(new RegExp("\\$" + paramName, "g"),paramValue);
      }
    }

    return found;
  } else {
    return this;
  }
}

/**
 * Convert a string to HTML entities
 */
String.prototype.toHtmlEntities = function() {
    return this.replace(/./gm, function(s) {
        return "&#" + s.charCodeAt(0) + ";";
    });
};

/**
 * Create string from HTML entities
 */
String.fromHtmlEntities = function(string) {
    return (string+"").replace(/&#\d+;/gm,function(s) {
        return String.fromCharCode(s.match(/\d+/gm)[0]);
    })
};

/**
 * Request a bunch of different info to the server. I know that usually those
 * "composed" services is not a good idea :-( but requesting all the info in a 
 * single request reduce the calls to the server
 */
function getPageInfo(options, onDone) {
  var thisPageInfo = {};

  // If we have already cached the i18n, do not request them
  var i18n = localStorage.getItem('__i18n__');
  if ( i18n ) {
    thisPageInfo['i18n']=0;  
  } else {
    thisPageInfo['i18n']=1;  
  }

  $.getJSON(
    BE_CONTEXT + '/service/GetPageInfo',
    thisPageInfo,
    function(data) {
      // Translate the page with the i18n received (this first time, build 
      // also the menu for selecting language )

      // We have received from server
      if ( data['i18n'] ) {
        localStorage.setItem('__i18n__', JSON.stringify(data['i18n']));
        translatePage(data['i18n'], true);
      // Use the cache
      } else {
        var i18n = JSON.parse(localStorage.getItem('__i18n__'));
        translatePage(i18n, true);
      }

      // Callback function 
      if ( onDone ) {
        onDone(data['user']);
      }
    }
  );
}

/**
 * Translate the page. 
 * @param data Struct with info coming from the server, containing translations, 
 *             list of languages,...
 * @param doBuildLangMenu If true, build the menu for selecting language
 */
function translatePage(data, doBuildLangMenu) {
  // Store the current values
  if ( data ) {
    TRANSLATIONS = data['i18n'];
    ALL_LANGS    = data['langs'];
    CURR_LANG    = data['currLang'];
  }

  // Build the menu with all the languages 
  if ( doBuildLangMenu ) {
    var $allLangs = $('#allLangs');

    renderData($allLangs, null);
    renderData($allLangs, ALL_LANGS, function($ele, data) {
      // When clicking, get the translation for that language and translate the 
      // entire page
      $ele.click(function() {
        $.getJSON(
          BE_CONTEXT + '/service/GetTranslations',
          { 'lang' : data['Locale'] },
          function(data) {
            translatePage(data, false);
          }
        );
      });
    });
  }

  // Set the right orientation
  var orientation='rtl';
  for(var ind=0; ind<ALL_LANGS.length; ++ind ) {
    if ( ALL_LANGS[ind]['Locale']==CURR_LANG ) {
      orientation=ALL_LANGS[ind]['Orientation'].toLowerCase();
      break;
    }
  }
  $('body').attr('dir', orientation);

  // Translate the page
  $('body')
    .find('._i18n')
    .each(function(){
      var $this=$(this);
      var key=$this.data('i18n');

      // If does not have the data key, add it
      if ( !key ) {
        key=$this.html().trim();
        $this.data('i18n', key);
      } 

      // Translate this element
      $this.html(key.translate());
    });
  
  // Translate also the tile
  document.title = document.title.translate() 
    

  // Set the texts used by the datepicker in the right language
  $.datepicker.setDefaults (
    {
      dayNamesMin: [ 
        "DayMinMo".translate(),
        "DayMinTu".translate(),
        "DayMinWd".translate(),
        "DayMinTh".translate(),
        "DayMinFr".translate(),
        "DayMinSa".translate(),
        "DayMinSu".translate()
      ],
      monthNames: [ 
        "Month01".translate(),
        "Month02".translate(),
        "Month03".translate(),
        "Month04".translate(),
        "Month05".translate(),
        "Month06".translate(),
        "Month07".translate(),
        "Month08".translate(),
        "Month09".translate(),
        "Month10".translate(),
        "Month11".translate(),
        "Month12".translate()
      ]
    }
  );   
}

/**
 * Show the buttons corresponding to the actions to which the user has permissions.
 * Some comments:
 * - The user can be an authenticated user or an anonymous one (in this case the 
 *   action's permission = "" and usr['permissions']=[] )
 * - The permissions can be also "runtime" permissions (I know, the name is not 
 *   very good). That is, the user can have a certain permissions (let's say to 
 *   modify a User) BUT not depending on certain runtime data (ex. if the user is
 *   in a certain status). That kind of checks must be done in the server.  
 * @param actionsCfg array of strcuts with all the info required to render the 
 * buttons
 *   {
 *      "url"  : '/webrad/fe/_Role_Permission/Add4Role_Role_Permission.html?' + 'Id_Role=' + actionData['Id_Role'],
 *      "name" : "_Role_Permission:Add4Role:Title".translate(),
 *      "askConfirmation" : "",
 *      "beOnly" : false,
 *      "permission" : "_Role_Permission:Add4Role",
 *      "goOnActionDone" : "refresh"
 *   }
 */
function buildGlobalActions($pGlobalActions, $pErrors, actionsCfg, usr) {
  // Remove all those actions that are not for this user
  if ( usr ) {
    // Those are the actions we are going to render from actionsCfg
    var actions2Render=[];
    // Some of the actionsCfg (the ones with attribute checkSecurity) need to
    // be checked in the server
    var actions2ServerCheck=[];

    for(var ind=0; ind<actionsCfg.length; ++ind) {
      var actionCfg = actionsCfg[ind];

      // To be more effidcient, independent of the fact the action has 
      // checkSucirty or not, it the user has NOT the permission, do NOT
      // ask to the server (to check the permission is a cech OBLIGATORY
      // in the server
      /*
      // User does NOT have permission
      if ( actionCfg['permission'] && 
           actionCfg['permission'].length > 0 &&
           usr['permissions'].indexOf(actionCfg['permission'])==-1 ) {
        actionsCfg.splice(ind, 1);
      } 
      */

      // If this action has checkSecurity that means the server will take care of
      // it
      if ( actionCfg['checkSecurity'] ) {
          actions2ServerCheck.push(actionCfg);
      // We can do a first analysis here and reject already some actions  
      }  else {
        // The action has no permission or the user has the permission, pass the FIRST filter
        if ( !actionCfg['permission'] || 
             actionCfg['permission'].length==0 ||
             usr['permissions'].indexOf(actionCfg['permission'])!=-1 ) {
          // We can still not add it to actions2Render because it has been checked
          // with the server, with the runtime parameters
          if ( actionCfg['checkSecurity'] ) {
            actions2ServerCheck.push(actionCfg);
          // No further checks, add it to the list
          } else {
            actions2Render.push(actionCfg);
          }
        }
      }
    }

    // Some of the actions still need to be checked against the server using the 
    // rutime information in a SECOND filter
    if ( actions2ServerCheck.length>0 ) {
      $.post(
        // @TODO : I do not know how to pass actions2ServerCheck to PHP without stringify :-(
        BE_CONTEXT + '/service/CheckActionsPermissions',
        {
          "actionsCfg" : JSON.stringify(actions2ServerCheck)
        },
        function(data) {
          // data conteins the actions that can be rendered because have passed
          // the server filter
          for(var ind=0; ind<data.length; ++ind ) {
            actions2Render.push(data[ind]);
          }
          renderGlobalActions($pGlobalActions, $pErrors, actions2Render);
        }
      );      
    } else {
      renderGlobalActions($pGlobalActions, $pErrors, actions2Render);
    }
  } 
} 

/**
 * Render the buttons
 */
function renderGlobalActions($pGlobalActions, $pErrors, actionsCfg) {
  // Show me the buttons!!!
  renderData(
    $pGlobalActions, 
    actionsCfg,
    function($row, rowData) {
      // To make easier to change the visual aspect of the buttons, add 
      // a class
      $row.addClass(rowData['actionName']);

      // When clicking on an action we must control:
      // + If needed, ask for a confimation before execute the action
      // + If is a beOnly, call the action with JSON and handle the OK/KO
      $row.find('a').on(
        "click", 
        { 
          "actionCfg" : rowData
        }, 
        function(event) {

          // Relax! We will do the job for you
          event.preventDefault();

          var actionCfg = event.data.actionCfg;
          
          // We have to ask first the user if he wants
          // Here we're going to use a modal config panel that is reused among 
          // ALL the actions
          if ( actionCfg['askConfirmation']  ) {
            var actionTitle = $(this).find('span').html();
            var $pAskConfirmation = $('#pAskConfirmation');

            // Put the i18n Messages
            $pAskConfirmation.find('.modal-title').html(actionTitle); 
            $pAskConfirmation.find('.modal-body').html(actionCfg['askConfirmation'].translate()); 

            // Remove previous listeners
            $pAskConfirmation.find('._btnYes').off("click");
            
            // Add the new listener, so when clicking to the Yes the right action
            // is peformed
            $pAskConfirmation.find('._btnYes').on("click", {"actionCfg" : event.data.actionCfg}, function(){
              var actionCfg = event.data.actionCfg;
              executeAction(actionCfg, $pErrors);
            });

            // Show it!
            $pAskConfirmation.modal('show');
          // mejor pedir disculpas que pedir permiso so, go ahead!!
          } else {
            executeAction(actionCfg, $pErrors);
          }
        } // click
      );
    } // function
  );
}

function askConfirmation(title, text, onYesAction) {
   var $pAskConfirmation = $('#pAskConfirmation');

   // Put the i18n Messages
   $pAskConfirmation.find('.modal-title').html(title); 
   $pAskConfirmation.find('.modal-body').html(text); 

   // Remove previous listeners
   $pAskConfirmation.find('._btnYes').off("click");
   
   // Add the new listener, so when clicking to the Yes the right action
   // is peformed
   $pAskConfirmation.find('._btnYes').on("click", {"actionCfg" : onYesAction}, function(event){
     var actionCfg = event.data.actionCfg;
     executeAction(actionCfg);
   });

   // Show it!
   $pAskConfirmation.modal('show');
}

/**
 * Executes an action
 */
function executeAction(actionCfg, $pErrors) {
  // In a new tab
  if ( actionCfg['whereOpenAction']=='new_tab' ) {
    window.open(actionCfg['url'],'_blank');
  } else if ( actionCfg['whereOpenAction']=='new_window' ) {
    window.open(actionCfg['url'],'_blank', 'location=yes');
  } else {
    // This action has not FE, so execute the BE via AJAX
    if ( actionCfg['beOnly'] ) {
      // @TODO : control OK/KO messages
      $.getJSON(actionCfg['url'], function(data){
        if ( data.errors )  {
          displayFormErrorMessages(data.errors, $pErrors);
          $('#pAskConfirmation').modal('hide');
          return;
        // After the action is done ok, what next?
        } else {
          if ( 'download-content' in data ) {
            var cfg = data['download-content'];
              
            var url=null;      
            if ( 'base64Encoded' in cfg && cfg['base64Encoded'] ) {
              url='data:' + cfg['mimetype'] +';base64,' + cfg['data'] ; 
            } else {
              url='data:' + cfg['mimetype'] +',' + escape(cfg['data']); 
            }       
            var link = document.getElementById("downloadLink");
            link.setAttribute("href", url);
            link.setAttribute("download", cfg['filename']);
            link.click();
          } else {
            var url; 

            // Go back
            if ( actionCfg['goOnActionDone']=='back' ) {
              url = document.referrer;
            // Refresh the current page    
            } else if ( actionCfg['goOnActionDone']=='refresh' ) {
              url = document.location.href;
            } else if ( actionCfg['goOnActionDone'] ) {
              url = actionCfg['goOnActionDone'];
            }

            // We have received an OK message in the response, add it in the url
            if ( 'msgOK' in data ) {
              storeMsgOK(data.msgOK.translate(data));
            }

            // Go to the next page
            document.location = url;
          }
        }         
      });
    // Go to the FE page  
    } else {
      document.location.href=actionCfg['url'];
    }
  }
}

function setItem(key, value) {
  localStorage.setItem(key, value);
}

function getItem(key) {
  return localStorage.getItem(key);
}

function removeItem(key) {
  localStorage.removeItem(key);
}

// -----------------------------------------------------------------------------
// Breadcrumb Management
// -----------------------------------------------------------------------------
function Breadcrumb(){
  // Properties
  this.propName = "__breadcrumb__";
  this.$container = $('#breadcrumb ol'); 

  // Methods
  this.getContent = function(){
    var data = localStorage.getItem(this.propName);
    var json = {};
    if ( data && data.length!=0 ) {
      json = JSON.parse(data); 
    }

    return json; 
  }

  this.setEntry = function(key, entry){
    var json = this.getContent();
    json[key] = entry;
    localStorage.setItem(this.propName, JSON.stringify(json));
  }


  // Order is:
  // electionType > contest
  this.render = function(list) {
    this.$container.empty();
    for (var ind = 0; ind<list.length; ++ind) {
      this.renderEntry(list[ind], ind===(list.length-1));
    }
  }

  this.renderEntry = function(key, isLast) {
    var data = this.getContent();
    var entryCfg = data[key];

    if ( entryCfg ) {
      var $li   = $('<li  class="phn"></li>');
      if ( isLast ) {
        $li.html(entryCfg['title'].toHtmlEntities());
      } else {
        var $a    = $('<a></a>').attr('href', entryCfg['url']).html(entryCfg['title'].toHtmlEntities());
        var $span = $('<span class="ci ci-chevron-right v-middle"></span>');
        
        $li.append($a);
        $li.append($span);        
      }

      this.$container.append($li);
    } 
  }
} 

// -----------------------------------------------------------------------------
// Tabbed Panels
// -----------------------------------------------------------------------------
// We would had a problem if two tabbed groups appera in the same page, 
// becasue they are not (as group) identified, but this is not the case now
function TabbedPanel(){
  // Methods
  this.recoverLastClick = function(){
    var propName = '__tabbedPanel__' + $('body').attr('id');
    
    // Do we have stored something for this page?
    var idx = localStorage.getItem(propName);
    if ( idx ) {
      var $a = $('ul.nav.nav-tabs > li').eq(idx).find('a'); 
      $a.trigger('click');
    }
  }

  this.rememberTheClicks = function(){
    $('ul.nav.nav-tabs > li > a').click(function(){
      var propName = '__tabbedPanel__' + $('body').attr('id');
      var idx = $(this).parent().index();
      localStorage.setItem(propName, idx);
    });
  }
}

// -----------------------------------------------------------------------------
// Controles independent checkbox in candidates
// -----------------------------------------------------------------------------
/**
 * We can select if a Candidate is independent or not (default No).
 * If it is NOT independedent AND the Candidatura belongs to a Coalition, for
 * every Candidate we have to choose the Party.
 */
function controlIndependentCheckbox(formId) {
$(formId).on("custom.dataLoaded", function(e, formData) {
  var $frm = $(this);
  
  // If it is NOT a Coalition, hide the select to choose the party
  if ( formData['typePoliticalGroup']!='COALICION' ) {
    $frm.find('div.IdPoliticalGroup').hide();
  }
  else {
    if ($('*[name=IsIndependent]').is(":checked")) {
        $('.IdPoliticalGroup').hide();
    }

    // The candidate is marked as independent or not
    $frm.find('*[name=IsIndependent]').change(function(){
      if ($(this).is(":checked")) {
        $('.IdPoliticalGroup').hide();
      }
      else {
        $('.IdPoliticalGroup').show();
      }
    });
  }

});

}

// -----------------------------------------------------------------------------
// Widget Loader
// -----------------------------------------------------------------------------
function showLoaderIfTooLong($ele, timeout) {
  var t = setTimeout(function(pWidget){
    showWidgetLoader(pWidget);
  }, !timeout ? 2000 : timeout, $ele);
  $ele.data('widget-loader-timeout', t);
}

function cancelLoader($ele) {
  var t = $ele.data('widget-loader-timeout');
  clearTimeout(t);
  hideWidgetLoader($ele);
}

function showWidgetLoader($ele) {
  $ele.find('.widget-loader').show();
}

function hideWidgetLoader($ele) {
  $ele.find('.widget-loader').hide();
}
