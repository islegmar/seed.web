<?php
/**
 * This file is include by everybody and choose the right configuration file
 * contained in the 'config/' folder'. This election can be done based on 
 * the hostname, a cookie, a URL parameter.....
 *
 * In a "real" programming language this should be a Controller.
 *
 * @Version : 1.0
 *
 * CHANGES
 */
?>
<?php
define ('APP_NAME', '{APP_NAME}');
define('APP_ROOT_DIR', dirname(__FILE__) . '/../');
// This is used in the code (logger auth) when logging messages to indicate the 
// application that logs them.
define('LOG_APP_NAME', '{APP_NAME}');

// ------------------------------------------------ Define some global variables
// The *_DIR variables are used when included something from PHP 
define('EXTERNAL_ROOT_DIR', APP_ROOT_DIR . '/include/external');
define('INTERNAL_ROOT_DIR', APP_ROOT_DIR . '/include/internal');

// ------------------------------------------------------ Specific configuration
// In order to avoid atacks, we have removed the host specific configuration
// Also de one deployed in the app itself has been removed because it is ok in 
// a local environment but it has no sense in a real one where the config 
// contains sensitive data and it is maintenad out of the app
/*
// Host specific 
if ( file_exists(APP_ROOT_DIR . '/php/config/' . $_SERVER['HTTP_HOST'] . '.php') ) {
  include_once(APP_ROOT_DIR . '/php/config/' . $_SERVER['HTTP_HOST'] . '.php');
// Default in the app
} elseif ( file_exists(APP_ROOT_DIR . '/php/config/default.php') ) {
  include_once(APP_ROOT_DIR . '/php/config/default.php');
// This is the most usual : the config out the app, so it can be maintenad
} else {
  include_once($_SERVER['DOCUMENT_ROOT'] . '/config/' . APP_NAME . '.php');
}
*/
if ( !file_exists($_SERVER['DOCUMENT_ROOT'] . '/config/' . APP_NAME . '.php') ) {
  throw new Exception('Missing configuration ');
} else {
  include_once($_SERVER['DOCUMENT_ROOT'] . '/config/' . APP_NAME . '.php');
}


// ----------------------------------------------- FactoryObject's Concifuration
$FACTORYOBJECT_CFG = array(
  'beans' => array(
    'FileManager' => array(
      'singleton' => true,
      'class'     => 'FileManager',
      'file'      => INTERNAL_ROOT_DIR . '/utils/FileManager.php',
      'cfg' => array (
        'dirBase' => $DEF_DATADIR
      )
    ),
    /* The default database connection (this starts automaticallyu a transaction
     * and it is also commit/rollback automatically when exit) */
    'DBConnection' => array(
        'singleton' => true,
        'class'     => 'DBConnection',
        'file'      => INTERNAL_ROOT_DIR . '/db/DBConnection.php',
        'cfg' => array (
            'server'  => MYSQL_SERVER_NAME,
            'user'    => MYSQL_DB_USERID,
            'password'=> MYSQL_DB_PASSWORD,
            'name'    => MYSQL_DB_NAME
        )
    ),
    'I18N' => array(
      'singleton' => true,
      'class'     => 'I18N',
      'file'      => APP_ROOT_DIR . '/php/utils/I18N.php',
      'cfg' => array (
        'defLang'  => 'es',
        'filesDir' => $DEF_DATADIR . '/i18n'  
      )
    ),
    'Crypto' => array(
      'singleton' => true,
      'class'     => 'Crypto',
      'file'      => APP_ROOT_DIR . '/php/utils/Crypto.php',
      'cfg' => array (
        'symmetricKey'  => '%$#erDwj!!@'  
      )
    ),
    /*
    'WebSession' => array(
      'singleton' => true,
      'class'     => 'WebSession',
      'file'      => INTERNAL_ROOT_DIR . '/utils/WebSession.php'
      'cfg' => array (
        'sessionName' => '__WebSession__' . APP_NAME . '__'
      )
    ),*/
    /* Anonymous User */
    'AnonymousPrincipal' => array(
      'class' => 'MyUsuario',
      'file'  => APP_ROOT_DIR . '/php/onegocio/MyUsuario.php'
    ),
    /* Non anoymous user */
    'Usuario' => array(
      'class' => '_User',
      'file'  => APP_ROOT_DIR . '/_User/onegocio/_User.php'
    ),
    /* Do not set the config value for onLoginUrl, use ALWAYS the one stored 
    in the database, to avoid unexpected behaviours (see LoginSrv 4+ìnfo) */ 
    'LoginSrv' => array(
      'singleton' => true,
      'class'     => 'LoginSrv',
      'file'      => INTERNAL_ROOT_DIR . '/service/LoginSrv.php'
    ),
    'AnonymousUserFilter' => array(
      'singleton' => true,
      'class'     => 'AnonymousUserFilter',
      'file'      => INTERNAL_ROOT_DIR . '/filter/AnonymousUserFilter.php',
      'cfg'       => array(
      )
    ),
    'WebApp' => array(
      'singleton' => true,
      'class'     => 'WebApp',
      'file'      => INTERNAL_ROOT_DIR . '/utils/WebApp.php',
      'cfg'       => array (
        // The order is important, because it is the order how the filters are applied
        'filters' => array( 
          'AnonymousUserFilter'
        )
      )
    ),
    '_ConfigApp' => array(
      'class'     => '_ConfigApp',
      'file'      => APP_ROOT_DIR . '/_ConfigApp/onegocio/_ConfigApp.php'
    )    
  ),
  'dirs'  => array(
    APP_ROOT_DIR ,
    APP_ROOT_DIR . '/*/onegocio',
    INTERNAL_ROOT_DIR,
    APP_ROOT_DIR . '/php/onegocio',
    APP_ROOT_DIR . '/php/onegocio/dao',
    APP_ROOT_DIR . '/php/service',
    APP_ROOT_DIR . '/php/controller',
    APP_ROOT_DIR . '/php/utils',
    INTERNAL_ROOT_DIR . '/service',
    INTERNAL_ROOT_DIR . '/controller',
    INTERNAL_ROOT_DIR . '/security',
    INTERNAL_ROOT_DIR . '/utils',
    INTERNAL_ROOT_DIR . '/etl'
  )
);


// -------------------- Perform the basic configuration that MUST BE DONE always
// First of all, the logger
include_once(INTERNAL_ROOT_DIR . '/utils/MyLogger.php');
MyLogger::config($LOG_CFG);

// Finally, the FactoryObject that will be the entry for all the objects
include_once(INTERNAL_ROOT_DIR . '/utils/FactoryObject.php');
FactoryObject::config($FACTORYOBJECT_CFG);

// @todo : we have checkit
// start the session
require_once(INTERNAL_ROOT_DIR . '/utils/WebSession.php');
WebSession::getInstance('__WebSession__' . APP_NAME . '__');

// ----------------------------------- Apply the filters in the incoming request
$webApp = FactoryObject::newObject('WebApp');
$webApp->applyFilters();

// ------------------------------------------------------ Utility/Global Methods
// NOT USE THEM

// -------------------------------------------------------- Deprecated functions
function __tr__($code, $vars=null, $values=null) {
  throw new Exception("This function is not in use anymore, review your code!!");
  // return FactoryObject::newObject('I18N')->translate($code, $vars, $values);
}

function __etr__($code, $vars=null, $values=null) {
  throw new Exception("This function is not in use anymore, review your code!!");
  // echo(__tr__($code, $vars, $values));
}

function __checkRole__($roles) {
  throw new Exception("This function is not in use anymore, review your code!!");
  // FactoryObject::newObject('SecurityUtil')->checkPrincipalRoles($roles);
}

function __checkPermission__($permissionName) {
  throw new Exception("This function is not in use anymore, review your code!!");
  // FactoryObject::newObject('SecurityUtil')->checkPermission($permissionName);
}

function __checkAuthenticated__() {
  throw new Exception("This function is not in use anymore, review your code!!");
  /*
  if ( WebSession::getInstance()->getPrincipal()->isAnonymous() ) {
    throw new Exception('Anonymous user can not acces');
  }
  */
}

function __includeCustomCode__($fullFile) {        
  throw new Exception("This function is not in use anymore, review your code!!");
  /*                      
  // IL - 28/01/2015 - Include custom code
  // This has sense when the app is created using the generator.
  // The files starting with '_' are generated code (every time the app is 
  // regenerated they are overwritten) and they can include some custom code that 
  // does NOT start by '_'  (every time the app is regenerated they are kept)

  $customFile=null;
  $file=basename($fullFile);               
  // Generated file                               
  if ( strrpos($file, '_', -strlen($file))!==FALSE ) {                    
    $customFile = dirname($fullFile) . '/' . substr($file, 1) . '.js.php';         
  } else {                                                                
    $customFile = $fullFile . '.js.php';                                           
  } 

  if ( file_exists($customFile) ) {
    include $customFile;
  }
  */
}

function __url__($uri, $base='') {
  throw new Exception("This function is not in use anymore, review your code!!");
  // echo  $base . $uri; (default value $base=APP_CONTEXT)
}

function __getUrl__($uri) {
  throw new Exception("This function is not in use anymore, review your code!!");
  // return APP_CONTEXT . $uri;
}
?>