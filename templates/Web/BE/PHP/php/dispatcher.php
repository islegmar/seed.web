<?php
/**
 * ALL the request go through this dispatcher. Its main function is to find 
 * a controller that handles the incoming request and pass it to it.
 */
?>
<?php
error_reporting(E_ALL);
// By security reasons, disable it by default
// @TODO : enable it when developing
// ini_set('display_errors', 1);
set_time_limit ( 1800 );

// First step : execute the config. That will make the startup of all the needed
// services, set global variables,....	
// @TODO : what to do if there is an error here?
require_once('./config.php');
require_once(INTERNAL_ROOT_DIR . '/utils/FactoryObject.php');

$logger=null;
$logger = Logger::getLogger("main");
if ( $logger->isDebugEnabled() ) {
	$logger->debug('Enter on ' . __FILE__ );
}

// IL - 27/01/2015 - This is done now by Dispatcher
$dispatcher = FactoryObject::newObject('Dispatcher');
$dispatcher->dispatch();
?>
